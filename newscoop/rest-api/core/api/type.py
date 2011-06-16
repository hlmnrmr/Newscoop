'''
Created on Jun 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the types used for APIs.
'''
from _abcoll import Iterable
from inspect import isclass
from newscoop.core.util import Uninstantiable
import logging
import numbers

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Type:
    '''
    The class that represents the API types used for mapping data.
    '''

    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
                The object instance to check.
        '''
        raise NotImplementedError('Override this method')
    
class TypeForClass(Type):
    '''
    Provides type class validating based on the provided class.
    '''
    
    def __init__(self, typeClass):
        '''
        Initializes the type for the provided type class.
        
        @param typeClass:class
            The class to be checked if valid.
        '''
        assert isclass(typeClass), 'Invalid class %s.' % typeClass
        self._typeClass = typeClass
        
    def getTypeClass(self):
        '''
        Provides the type class of this type.
        @return: class
            The assigned class of this type.
        '''
        return self._typeClass

    def isValid(self, obj):
        return isinstance(obj, self._typeClass)
    
    def __str__(self):
        return '<TypeClass[%s.%s]>' % (self._typeClass.__module__, self._typeClass.__name__)

class TypeHolder:
    '''
    Provides a type container for classes. It used by the models to provide a type based on their class, very
    helpful when the model extends another model. 
    '''

    @classmethod
    def getType(cls):
        '''
        Provide the type based on the provided class.

        @return: Type
            The type of the holder.
        '''
        raise NotImplementedError('Override this method')

class TypeHolderBasic(TypeHolder):
    '''
    Type holder that provides the type from the '_type' class attribute.
    '''
    
    @classmethod
    def getType(cls):
        return cls._type
    
# --------------------------------------------------------------------

class Boolean(Uninstantiable, TypeHolderBasic):
    '''
    Maps the boolean values.
    Only used as a class, do not create an instance.
    '''
    #DO NOT Change this field, since it represents the type.
    _type = TypeForClass(bool)
    
class Integer(Uninstantiable, TypeHolderBasic):
    '''
    Maps the integer values.
    Only used as a class, do not create an instance.
    '''
    #DO NOT Change this field, since it represents the type.
    _type = TypeForClass(int)

class Number(Uninstantiable, TypeHolderBasic):
    '''
    Maps the numbers, this includes integer and float.
    Only used as a class, do not create an instance.
    '''
    #DO NOT Change this field, since it represents the type.
    _type = TypeForClass(numbers.Number)

class String(Uninstantiable, TypeHolderBasic):
    '''
    Maps the string values.
    Only used as a class, do not create an instance.
    '''
    #DO NOT Change this field, since it represents the type.
    _type = TypeForClass(str)
    
# --------------------------------------------------------------------
    
class List(Type):
    pass

# --------------------------------------------------------------------

class Types(Type, Iterable):
    '''
    This class is basically a collection of Type(s).
    It used to wrap several types in order to perform checking on data sets.
    '''
    
    def __init__(self, types):
        '''
        Constructs a type set for the provided type set.
        
        @param typeSet: iterable|type|None
            The type or types to be described by this set, can be even None for a empty type set.
        '''
        self._types = []
        if isclass(types):
            self._types.append(asType(types))
        elif isinstance(types, Iterable):
            for type in types:
                self._types.append(asType(type))
        elif not types is None:
            raise AssertionError('The types set needs to be a type or collection of types, provide None if an empty type set is required')
        self._types = tuple(self._types)
        
    def isValid(self, obj):
        '''
        Checks if the provided sequence of object instances is represented
        by this set of API types.
        
        @param obj: tuple|obj
                The object instances sequence to check.
        '''
        if isinstance(obj, tuple):
            if not len(obj) == len(self._types):
                return False
            for type, value in zip(self._types, obj):
                if not type.isValid(value):
                    return False
        elif len(self._types) == 1:
            if not self._types[0].isValid(obj):
                return False
        else:
            if not obj is None:
                return False
        return True
            
    def __len__(self):
        '''
        Provides the number of types that this type set contains.
        
        @return: int
            The number of types contained.
        '''
        return len(self._types)
    
    def __iter__(self):
        for type in self._types:
            yield type
            
    def __str__(self):
        return '<Types[%s]>' % ', '.join([str(type) for type in self])

# --------------------------------------------------------------------

class PropertyType(Type):
    '''
    This type is used to wrap model property as types. So whenever a type is provided based on a Model property
    this type will be used. Contains the type that is reflected based on the property type also contains the 
    Property and the Model class that is constructed on. This type behaves as the type assigned to the property 
    and also contains the references to the property and model class.
    '''
    
    def __init__(self, modelClass, property):
        '''
        Constructs the model type for the provided property and model class.
        
        @param modelClass: class
            The model class of the type.
        @param property: Property
            The property that this type is constructed on.
        '''
        from newscoop.core.api.operator import Property, Model
        assert issubclass(modelClass, Model), 'Invalid model class %s' % modelClass
        assert isinstance(property, Property), 'Invalid property %s' % property
        self._modelClass = modelClass
        self._property = property
        
    def getModelClass(self):
        '''
        Provides the model class that this type is constructed on.
        
        @return: class
            The model class of the type.
        '''
        return self._modelClass
    
    def getProperty(self):
        '''
        Provides the property that this type is constructed on.
        
        @return: Property
            The property of the type.
        '''
        return self._property

    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
                The object instance to check.
        '''
        return self._property.getType().isValid(obj)

    def __str__(self):
        return '<ModelType[%s]>' % self._property

# --------------------------------------------------------------------

def asType(type):
    '''
    First checks if the provided parameter is not already an instance of a Type.
    If not it will provides the conversion to an instance if that type is singletone.
    In order to attach types to classes you just need to provide them as a class attribute
    under the name '_type'.

    @param type: Type|class
    '''
    if isclass(type):
        if type == bool:
            return Boolean.getType()
        elif type == int:
            return Integer.getType()
        elif type == float:
            return Number.getType()
        elif type == numbers.Number:
            return Number.getType()
        elif type == str:
            return String.getType()
        elif issubclass(type, TypeHolder):
            type = type.getType()
        else:
            raise AssertionError('Invalid class %s provided, it should at least extend TypeHolder' % type)
    assert isinstance(type, Type), 'Invalid instance %s, is not of a Type class' % type
    return type

