'''
Created on Jun 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides classes that provide general behaviour or functionality.
'''

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
        raise AssertionError('Cannot create an instance of "' + str(cls.__name__) + '" class');

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
            cls.__instance = super().__new__(cls);
        return cls.__instance

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
