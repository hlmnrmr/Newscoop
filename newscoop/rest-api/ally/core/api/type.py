'''
Created on Jun 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the types used for APIs.
'''
from _abcoll import Iterable, Sized, Iterator
from inspect import isclass
from ally.core.util import Uninstantiable, simpleName, Singletone, guard
import abc
import logging
import numbers

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@guard
class Type(metaclass=abc.ABCMeta):
    '''
    The class that represents the API types used for mapping data.
    '''
    
    def __init__(self, isPrimitive):
        '''
        Initializes the type setting the primitive aspect of the type.
        
        @param isPrimitive: boolean
            If true than this type is considered of a primitive nature, meaning that is an boolean, integer,
            string, float ... .
        '''
        self.isPrimitive = isPrimitive

    @abc.abstractmethod
    def forClass(self):
        '''
        Provides the basic class representation of the type.
        
        @return: class|None
            The class represented by the type, None if not available.
        '''

    @abc.abstractmethod
    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
                The object instance to check.
        '''

class TypeClass(Type):
    '''
    Provides type class validating based on the provided class.
    '''
    
    def __init__(self, forClass, isPrimitive=False):
        '''
        Initializes the type for the provided type class.
        @see: Type.__init__
        
        @param forClass:class
            The class to be checked if valid.
        '''
        assert isclass(forClass), 'Invalid class %s.' % forClass
        self._forClass = forClass
        super().__init__(isPrimitive)

    def forClass(self):
        '''
        @see: Type.forClass
        '''
        return self._forClass
        
    def isValid(self, obj):
        '''
        @see: Type.isValid
        '''
        return isinstance(obj, self._forClass)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._forClass == other._forClass
        return False
    
    def __str__(self):
        return simpleName(self._forClass)

# --------------------------------------------------------------------

class TypeNone(Singletone, Type):
    '''
    Provides the type that matches None.
    '''
    def __init__(self):
        '''
        @see: Type.__init__
        '''
        super().__init__(True)

    def forClass(self):
        '''
        @see: Type.forClass
        '''
        return None
    
    def isValid(self, obj):
        '''
        @see: Type.isValid
        '''
        return obj is None
    
    def __eq__(self, other):
        return isinstance(other, TypeNone)
    
    def __str__(self):
        return 'None'

class TypeId(TypeClass):
    '''
    Provides the type for the id. This type has to be a primitive type always.
    '''
    
    def __init__(self, forClass):
        '''
        Constructs the id type for the provided class.
        @see: TypeClass.__init__
        
        @param forClass: class
            The class that this type id is constructed on.
        '''
        super().__init__(forClass, True)

# --------------------------------------------------------------------

class Non(Uninstantiable):
    '''
    Maps the None type.
    '''
    #DO NOT Change this field, since it represents the type.
    api_type = TypeNone()
    
class Boolean(Uninstantiable):
    '''
    Maps the boolean values.
    Only used as a class, do not create an instance.
    '''
    #DO NOT Change this field, since it represents the type.
    api_type = TypeClass(bool, True)
    
class Integer(Uninstantiable):
    '''
    Maps the integer values.
    Only used as a class, do not create an instance.
    '''
    #DO NOT Change this field, since it represents the type.
    api_type = TypeClass(int, True)

class Number(Uninstantiable):
    '''
    Maps the numbers, this includes integer and float.
    Only used as a class, do not create an instance.
    '''
    #DO NOT Change this field, since it represents the type.
    api_type = TypeClass(numbers.Number, True)

class String(Uninstantiable):
    '''
    Maps the string values.
    Only used as a class, do not create an instance.
    '''
    #DO NOT Change this field, since it represents the type.
    api_type = TypeClass(str, True)

class Id(Uninstantiable):
    '''
    Maps the id values.
    Only used as a class, do not create an instance.
    '''
    #DO NOT Change this field, since it represents the type.
    api_type = TypeId(int)

# --------------------------------------------------------------------

class Iter(Type):
    '''
    Maps an iterator of values.
    You need also to specify in the constructor what elements this iterator will contain.
    Since the values in an iterator can only be retrieved once than this type when validating the iterator it will
    not be able to validate also the elements.
    '''
    
    def __init__(self, type):
        '''
        Constructs the iterator type for the provided type.
        @see: Type.__init__
        
        @param type: Type|class
            The type of the iterator.
        '''
        assert not isinstance(type, Iter), 'Invalid item type %s because is another iterable' % type
        self.itemType = typeFor(type)
        super().__init__(False)
    
    def forClass(self):
        '''
        @see: Type.forClass
        '''
        return self.itemType.forClass()

    def isValid(self, list):
        '''
        @see: Type.isValid
        '''
        if isinstance(list, Iterator) or isinstance(list, Iterable):
            return True
        return False
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.itemType == other.itemType
        return False
    
    def __str__(self):
        return '%s(%s)' % (simpleName(self), self.itemType)
    
class List(Iter):
    '''
    Maps lists of values.
    You need also to specify in the constructor what elements this list will contain.
    Unlike the iterator type the list type also validates the contained elements.
    '''
    
    def __init__(self, type):
        '''
        Constructs the list type for the provided type.
        @see: Iter.__init__
        '''
        super().__init__(type)
        

    def isValid(self, list):
        '''
        @see: Type.isValid
        '''
        if isinstance(list, Iterable) and isinstance(list, Sized):
            for obj in list:
                if not self.itemType.isValid(obj):
                    return False
            return True
        return False

# --------------------------------------------------------------------

class TypeModel(TypeClass):
    '''
    Provides the type for the model.
    '''
    
    def __init__(self, model):
        '''
        Constructs the model type for the provided model.
        @see: TypeClass.__init__
        
        @param model: Model
            The model that this type is constructed on.
        '''
        from ally.core.api.operator import Model
        assert isinstance(model, Model), 'Invalid model provided %s' % model
        self.model = model
        super().__init__(model.modelClass, False)

class TypeQuery(TypeClass):
    '''
    Provides the type for the query.
    '''
    
    def __init__(self, query):
        '''
        Constructs the query type for the provided query.
        @see: Type.__init__
        
        @param query: Query
            The query that this type is constructed on.
        '''
        from ally.core.api.operator import Query
        assert isinstance(query, Query), 'Invalid query provided %s' % query
        self.query = query
        super().__init__(query.queryClass, False)

class TypeProperty(Type):
    '''
    This type is used to wrap model property as types. So whenever a type is provided based on a Model property
    this type will be used. Contains the type that is reflected based on the property type also contains the 
    Property and the Model that is constructed on. This type behaves as the type assigned to the property 
    and also contains the references to the property and model class.
    '''
    
    def __init__(self, model, property):
        '''
        Constructs the model type for the provided property and model.
        @see: Type.__init__
        
        @param model: Model
            The model of the type.
        @param property: Property
            The property that this type is constructed on.
        '''
        from ally.core.api.operator import Property, Model
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(property, Property), 'Invalid property %s' % property
        assert isinstance(property.type, Type), 'Invalid property type %s' % type
        self.model = model
        self.property = property
        super().__init__(property.type.isPrimitive)

    def forClass(self):
        '''
        @see: Type.forClass
        '''
        return self.property.type.forClass()
    
    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
                The object instance to check.
        '''
        return self.property.type.isValid(obj)
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.model == other.model and self.property == other.property
        return False

    def __str__(self):
        return '%s.%s' % (self.model.name, self.property.name)

# --------------------------------------------------------------------

@guard
class Input:
    '''
    Provides an input entry for a call, this is used for keeping the name and also the type of a call parameter.
    '''
    
    def __init__(self, name, type):
        '''
        Construct the input.
        
        @param name: string
            The name of the input.
        @param type: Type
            The type of the input.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(type, Type), 'Invalid type %s' % type
        self.name = name
        self.type = type
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.type == other.type
        return False

    def __str__(self):
        return '%s=%s' % (self.name, self.type)

# --------------------------------------------------------------------

def typeFor(obj, type=None):
    '''
    If the type is provided it will be associate with the obj, if the type is not provided than this function
    will try to provide if it exists the type associated with the obj, or check if the obj is not a type itself and
    provide that.
    
    @param obj: object
        The class to associate or extract the model.
    @param type: Type
        The type to associate with the obj.
    @return: Type|None
        If the type has been associate then the return will be none, if the type is being extracted it can return
        either the Type or None if is not found.
    '''
    if type is None:
        type = getattr(obj, 'api_type', None)
        if type is None:
            if obj is None:
                return Non.api_type
            if isclass(obj):
                if obj == bool:
                    return Boolean.api_type
                elif obj == int:
                    return Integer.api_type
                elif obj == float:
                    return Number.api_type
                elif obj == numbers.Number:
                    return Number.api_type
                elif obj == str:
                    return String.api_type
            if isinstance(obj, Type):
                type = obj
        return type
    assert isinstance(type, Type), 'Invalid type %s' % type
    assert 'api_type' not in obj.__dict__, 'Already has a type %s' % obj
    setattr(obj, 'api_type', type)
