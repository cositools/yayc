import logging
logger = logging.getLogger(__name__)

import yaml

from pathlib import Path

class Configurator:
    """
    Access to configuration parameters. 

    The parameters are organized in nested dictionarys. They set values
    can be a number, a string or a list. They can be accessed as e.g. 
    :code:`config['group:subgroup:subsubgroup:parameter']`
    
    Parameters
    ----------
    config : dict
        Loaded yaml file
    config_path: Path
        Location of this config file. If None, absolute_path will return paths
        relative to the current working directory
    """

    def __init__(self, config = None, config_path = None):

        self._config = config

        if config_path is None:
            self._config_dir = Path.cwd()
            self._config_path = None
        else:
            self._config_path = Path(config_path)
            self._config_dir = self.config_path.parent

        # This allows use subconfig[] to get a new config, not
        # the value
        self.subconfig = self._subconfig(self)

    @property
    def config_path(self):
        return self._config_path

    @config_path.setter
    def config_path(self, config_path):
        self._config_path = Path(config_path)
        self._config_dir = self.config_path.parent

    @classmethod
    def open(cls, config_path):

        config_path = Path(config_path)

        with open(config_path) as f:
            config = yaml.safe_load(f)

        new = cls(config, config_path)

        logger.info("Using configuration file at %s", config_path)

        return new
            
    def __getitem__(self, key):

        value = self._config

        keys = key.split(':')
        
        for n,key in enumerate(keys):

            try:
                value = value[key]
            except KeyError:
                raise KeyError("Parameter '{}' doesn't exists".\
                               format(":".join(keys[:n+1])))
                
        return value
        
    def __setitem__(self, key, value):

        keys = key.split(':')
        
        elem = self._config

        for n,key in enumerate(keys[:-1]):

            if key not in elem:
                raise KeyError("Parameter '{}' doesn't exists".\
                               format(":".join(keys[:n+1])))
            
            elem = elem[key]

        if keys[-1] not in elem:
            raise KeyError("Parameter '{}' doesn't exists".\
                           format(":".join(keys)))
            
        elem[keys[-1]] = value

    def get(self, key, default = None):
        """
        Returns the value for key in the config. If not found returns a default value.

        Parameters
        ----------
        key :  str
            Key

        default
            default value
        """

        try:
            value = self[key]
        except KeyError:
            value = default
 
        return value

    class _subconfig:
        """
        See self.subconfig = self._subconfig(self) in the
        main class __init__
        """

        def __init__(self, config):
            self._main_config = config

        def __getitem__(self, key):

            config = Configurator(self._main_config[key])

            config._config_dir = self._main_config._config_dir
            config._config_path = self._main_config._config_path

            return config

    def override(self, *args):
        """
        Override one or more parameter by parsings strings of the form
        :code:`'group:subgroup:parameter = value'`. Value is parsed the same way
        as yaml would do it, so if it is a string use quotes. 

        The foreseen use case scenario is to let the uses override parameters 
        from command line e.g. :code:`--override "group:parameter = new_value"`.
        Note that the values can be overridden directly in code by using
        :code:`config['group:parameter'] = new_value"`.

        Parameters
        ----------
        args : string, array
            String(s) to parse and override parameters. 
        """
        
        if len(args) == 1:
        
            if isinstance(args[0], str):
                # Standard, single key
                key,value = args[0].split("=")

                self[key.strip()] = yaml.safe_load(value.strip())

            else:
                #Recursive
                for arg in args[0]:
                    self.override(arg)

        else:
            #Recursive
            for arg in args:
                self.override(arg)
            

    def absolute_path(self, path):
        """
        Turn a path relative to the location of the config file absolute

        Parameters
        ----------
        path: Path
            Relative path

        Returns
        -------
        Path
        """

        path = Path(path).expanduser()

        if path.is_absolute():
            return path
        else:
            return (self._config_dir / path).resolve()

    def dump(self, *args, **kwargs):
        """
        Dump the configuration contents to a file or a string.

        Parameters
        ----------
        args, kwargs
            All arguments are passed to yaml.dump(). By default it returns as 
            string. You can specify a file or stream to dump it into in the
            first argument.
        """
        
        return yaml.dump(self._config, *args, **kwargs)
        
