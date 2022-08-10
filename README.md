# yayc

Yet another YAML-based configurator library. Meant for BurstCube and the COSI Telescope, but maybe useful for other projects. 

## Reading a config file


```python
from yayc import Configurator
import yayc.test_data

c = Configurator.open(yayc.test_data.path/"config_example.yaml")
```


```python
c['section:param_int']
```




    1




```python
c['section:param_float']
```




    1.0




```python
c['section:param_string']
```




    'a'




```python
c['section:param_list']
```




    [0, 1, 2, 3]




```python
c['section:param_list2']
```




    ['a', 'b', 'c']



## Overriding a parameter

Usually you have command line programs like this
```
my_app -c config_example.yaml --foo bar
```

You might want to let the user to change the behavior, but also don't want to set a bunch of flags for each option. It's also cumbersome to modify the config file for each run. 

You can have a generic flag that the user can use to change any behavior, e.g.

```
my_app -c config_example.yaml --override "section:param_int = 2" "section:param_string = b"
```

You can parse this using `argparse` and pass the input to `--override` to the `Configurator` object:


```python
override_input = ["section:param_int = 2", "section:param_string = b"]
```


```python
c.override(*override_input)
```


```python
c["section:param_int"]
```




    2




```python
c['section:param_string']
```




    'b'



## Relative paths

It is usually desirable to keep other configuration files together with the yaml file and other logs. this makes it easier to reproduce results. To facilitate this, always use paths relative **to the config file**, not relative to where you executed the progam. Then use this:  


```python
c.absolute_path(c['section:param_path'])
```




    PosixPath('/Users/israel/work/software/yayc/yayc/test_data/my_file.txt')



## Logs

It's good practice to dump the config file, after any override, to the logs:


```python
with open('test.log', 'w') as f:
    f.write(c.dump())
```

## Dynamic initialization

This is a little more advanced. In general, you can initialize any object on the fly if you know the module, the name of the class and the input parameters. We can use this to dynamically instantiate an object of an arbitrary class:


```python
# Creating dummy classes in the current module (__main__)
    
import __main__

class ClassA:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
    
    def __repr__(self):
        return f"ClassA(args = {self._args}, kwargs = {self._kwargs})"
    
class ClassB:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
    
    def __repr__(self):
        return f"ClassB(args = {self._args}, kwargs = {self._kwargs})"
```

Initialize the objet on the fly


```python
objects = {label:getattr(__main__, params['class'])(*params['args'], **params['kwargs']) for label,params in c['dynamic_init'].items()}
```


```python
print(objects)
```

    {'objectA': ClassA(args = (1, 'a'), kwargs = {'foo': 2, 'bas': 'b'}), 'objectB': ClassB(args = (), kwargs = {'foo': 3})}

