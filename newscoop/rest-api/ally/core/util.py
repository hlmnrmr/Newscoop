'''
Created on Jun 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides classes that provide general behaviour or functionality.
'''
from _abcoll import Iterable
from inspect import isclass
import inspect
import sys

# --------------------------------------------------------------------

# Flag indicating if the guarding should be enabled.
GUARD_ENABLED = __debug__

# --------------------------------------------------------------------

class Uninstantiable:
    '''
    Extending this class will not allow for the creation of any instance of the class.
    This has to be the first class inherited in order to properly work.
    '''
    
    def __new__(cls, *args, **keyargs):
        '''
        Does not allow you to create an instance.
        '''
        raise AssertionError('Cannot create an instance of "' + str(cls.__name__) + '" class')

# --------------------------------------------------------------------

class Singletone:
    '''
    Extending this class will always return the same instance.
    '''
    
    def __new__(cls):
        '''
        Will always return the same instance.
        '''
        if not hasattr(cls, '__instance'):
            cls.__instance = super().__new__(cls)
        return cls.__instance

# --------------------------------------------------------------------

class Protected:
    '''
    Extending this class will not allow for the creation of any instance of the class outside the module that has
    defined it.
    This has to be the first class inherited in order to properly work.
    '''
    
    def __new__(cls, *args, **keyargs):
        '''
        Does not allow you to create an instance outside the module of the class.
        '''
        if not _isSameModule(cls):
            raise AssertionError('Cannot create an instance of "' + str(cls.__name__) + \
                                 '" class from outside is module')
        return super().__new__(cls, *args, **keyargs)

# --------------------------------------------------------------------

def guard(*args, **keyargs):
    '''
    Provides if in debug mode a guardian for the decorated class. A guardian is checking if there are illegal calls to the guarder class.
    Illegal calls are classified as being calls to protected attributes or method (does that start with '_') and
    also whenever you try to change outside the class or super class a public attribute that already has a value.
    How to use:
    
    @guard
    class MyClass
    'In this case all rules apply'
    
    @guard(ifNoneSet='myName')
    class MyClass
    'In this case all rules apply except if the public attribute myName has a None value it is possible to assign a
    not None value only once'
    
    @guard(allow='myName')
    class MyClass
    'In this case all rules apply except for the public attribute myName which can be changed from anywhere'
    '''
    if len(args) == 1:
        if GUARD_ENABLED:
            return _guardClass(args[0])
        else:
            return args[0]
    elif len(keyargs) > 0:
        def guardClass(clazz):
            return _guardClass(clazz, keyargs)
        return guardClass
    else:
        raise AssertionError('Invalid arguments %s' % keyargs.keys())

class Guardian:
    '''
    Provides the guardian implementation. A guardian is checking if there are illegal calls to the guarder class.
    Illegal calls are classified as being calls to protected attributes or method (does that start with '_') and
    also whenever you try to change outside the class or super class a public attribute that already has a value.
    '''
        
    def __getattribute__(self, name):
        if name.startswith('_') and not name.startswith('__'):
            if not (_isSameModule(self) or _isSuperCall(self)):
                raise AssertionError('Illegal call, the (%s) is protected' % name)
        return super().__getattribute__(name)
        
    def __setattr__(self, name, value):
        check = False
        if name.startswith('_'):
            check = True
        else:
            try:
                oldValue = self.__dict__[name]
                check = True
            except KeyError:
                pass
            if check:
                protect = self.__class__.protect_class
                if oldValue is None and 'ifNoneSet' in protect:
                    if name == protect['ifNoneSet'] or name in protect['ifNoneSet']:
                        check = False
                if 'allow' in protect:
                    if name == protect['allow'] or name in protect['allow']:
                        check = False
        if check and not _isSuperCall(self):
            raise AssertionError(('Illegal call, attribute (%s) from %s can be' + 
                                 ' changed only from class or super class') % (name, self))
        super().__setattr__(name, value)
       
    def __delattr__(self, name):
        if not self.isSuperCall():
            raise AssertionError(('Illegal call, attribute (%s) from %s can be' + 
                                 ' deleted only from class or super class') % (name, self))
        super().__delattr__(name)

# --------------------------------------------------------------------

def injected(clazz):
    '''
    Decorator for providing support for injecting.
    '''
    newClazz = type(clazz.__name__, (Injected, clazz), {})
    newClazz.__module__ = clazz.__module__
    return newClazz

class Injected:
    '''
    Provides the support for classes that are injected.
    '''
    
    @classmethod
    def __new__(cls, *args):
        '''
        Constructs the instance of the injected class.
        '''
        obj = super().__new__(cls)
        return obj
    
    def __init__(self, *args, **keyargs):
        '''
        Overriding initialization.
        '''
        self._arguments = (args, keyargs)

    def initialize(self):
        '''
        Method called by the IoC, after the properties finalizations.
        We will validate the object types that are found as class attributes and contain classes.
        '''
        args, keyargs = self._arguments
        super().__init__(*args, **keyargs)

def initialize(service):
    '''
    In case of injected resource it will initialize it.
    '''
    init = getattr(service, 'initialize', None)
    if init is not None:
        init()

# --------------------------------------------------------------------

def withPrivate(mainClass):
    '''
    Used a class decorator, what this will allow is the use of a inner class in a main class
    as a container of private attributes and methods.
    As an example:
        
        @withPrivate
        class Ordered:
        
            class private(Criteria):
                
                def _register(self, name):
                    print(name)
            
        def order(self):
             self.private._register('hy')
             
    So in the class Order we have the _register method as being private (still can be called from other classes)
    but is just grouped in a specific class so it whon't show up at type hinting.  This decorator will combine
    the main class and private class into one and also set as an attribute as self.private = self so you can
    actually have type hinting and functionality.
    
    P.S. Only used this class when is really needed since it might create confusions, use whenever you can the '_'
        convention.
    
    @param mainClass: class
        The class that will be merged with the private inner class.
    '''
    privateClass = mainClass.private
    del mainClass.private # remove it because will be mixed with the main class
    
    def __init__(self, *args, **keyargs):
        self.private = self

    return type(mainClass.__name__, (mainClass, privateClass), {'__init__': __init__})

# --------------------------------------------------------------------

def findInValues(dictionary, value):
    '''
    Searches in the provided dictionary the value as an entry in the dictionary values.
    
    @param dictionary: dictionary
        The dictionary to search the values.
    @param value: object
        The value to search in the dictionary values.
    @return: key|None
        Either the found key, or None.
    '''
    assert isinstance(dictionary, dict), 'Invalid dictionary %s' % dictionary
    for key, values in dictionary.items():
        if value in values:
            return key

# --------------------------------------------------------------------

def fullyQName(obj):
    '''
    Provides the fully qualified class name of the instance or class provided.
    
    @param obj: class|object
        The class or instance to provide the fully qualified name for.
    '''
    if not isclass(obj):
        obj = obj.__class__
    return obj.__module__ + '.' + obj.__name__

def simpleName(obj):
    '''
    Provides the simple class name of the instance or class provided.
    
    @param obj: class|object
        The class or instance to provide the simple class name for.
    '''
    if not isclass(obj):
        obj = obj.__class__
    return obj.__name__

def classForName(name):
    '''
    Provides the class for the provided fully qualified name of a class.
    
    @param name: string
        The fully qualified class name,
    @return: class
        The class of the fully qualified name.
    '''
    parts = name.split(".")
    module_name = ".".join(parts[:-1])
    class_name = parts[-1]
    if module_name == "":
        return __import__(class_name)
    else:
        __import__(module_name)
        return getattr(sys.modules[module_name], class_name)
    
# --------------------------------------------------------------------

def _guardClass(clazz, protect=None):
    assert isclass(clazz), 'Invalid class provided %s' % clazz
    if GUARD_ENABLED:
        if not issubclass(clazz, Guardian):
            protect = protect or {}
            newClazz = type(clazz.__name__, (clazz, Guardian), {})
            newClazz.__module__ = clazz.__module__
            clazz = newClazz
        else:
            assert protect is not None, \
            'Class %s already guarded and there are no other options beside the inherited class' % clazz
            old = clazz.protect_class
            for name, value in old.items():
                if name in protect:
                    if isinstance(value, Iterable):
                        if isinstance(protect[name], Iterable):
                            protect[name] = value + protect[name]
                        else:
                            protect[name] = value + [protect[name]]
                    else:
                        if isinstance(protect[name], Iterable):
                            protect[name] = [value] + protect[name]
                        else:
                            protect[name] = [value, protect[name]]
                else:
                    protect[name] = value
        clazz.protect_class = protect
    return clazz

def _isSameModule(obj):
    if not isclass(obj):
        obj = obj.__class__
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    try:
        return calframe[2][1] == sys.modules[obj.__module__].__file__
    except:
        return False

def _isSuperCall(obj):
    if not isclass(obj):
        obj = obj.__class__
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    for k in range(2, len(calframe)):
        locals = calframe[k][0].f_locals
        if 'self' in locals:
            if isinstance(locals['self'], obj):
                return True
    return False
    
