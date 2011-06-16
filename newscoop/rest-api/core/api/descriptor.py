'''
Created on Jun 14, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the descriptors used for API models.
'''

import logging
from newscoop.core.api.type import asType, PropertyType
from newscoop.core.api.operator import Property, Model, Query, Criteria, \
    Condition

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class APIProperty:
    
    '''
    Used to describe fields in models that are used by the APIs as properties.
    The model field described will validate the value and place it on the model object, it will do the same for 
    reading. By convention the descriptor will create in the attributes of the model instance  a variable called 
    '__prop_{descriptor name}' so for the example below the variable will be named '__prop_name'.
    
    ex:
        @APIModel()
        class Entity:
        
            name = APIProperty(str)
    '''
    
    def __init__(self, type):
        '''
        Constructs the API property descriptor.
        
        @param type: Type|class
            The type of the API property.
        '''
        self._type = asType(type)
        self._typesByClass = {}
        
    def _initializeInstance(self, byClass, name):
        '''
        TO BE USED ONLY BE SPECIALLY DESIGNED CLASSES.
        Initialize the property instance by providing the name under which the property has been declared.
        
        @param name: string
            The name under which the property has been declared in the model class.
        '''
        assert not hasattr(self, '_property'), 'Already initialized'
        assert isinstance(name, str), 'Invalid string %s for name' % name
        self._property = Property(name, self._type)
        log.debug('Registered property %s for class %s', self._property, byClass)
        
    def _validate(self, instance):
        '''
        Internal method used for validating the provided instance.
        '''
        assert isinstance(instance, Model), \
        'Invalid model %s, maybe you forgot to decorate with APIModel?' % instance
        assert self.getProperty() in instance.getProperties(), \
        'Invalid model %s does not contain this %s property' % (instance, self.getProperty())
        return True
        
    def getProperty(self):
        '''
        Provides the property that this descriptor is constructed on.
        
        @return: Property
            The property of the descriptor.
        '''
        try: return self._property
        except AttributeError:
            raise AssertionError('Not initialized %s, maybe you forgot to decorate the model with APIModel?' % self)
    
    def __get__(self, instance, owner):
        '''
        USED BY DESCRIPTORS.
        Called to get attributes from an instance or a class (owner).
        If fetched from a class, instance will be None.
        
        @param instance: object
            The owner instance, None if the owner is the class.
        @param owner: class 
            The owner class.
        '''
        if instance is None:
            assert issubclass(owner, Model), 'Invalid owner class %' % owner
            name = owner.__module__ + '.' + owner.__name__
            if not name in self._typesByClass:
                self._typesByClass[name] = PropertyType(owner, self.getProperty())
                log.debug('Created type for property %s for class %s', self._property, owner)
            return self._typesByClass[name]
        assert self._validate(instance)
        return self.getProperty().get(instance)
        
    def __set__(self, instance, value):
        '''
        USED BY PYTHON DESCRIPTORS.
        Called to set the attribute on an instance of the owner class to a new value.
        
        @param instance: object
            The instance, None if the owner is the class.
        @param value: object
            The value to set.
        '''
        assert self._validate(instance)
        self.getProperty().set(instance, value)

    def __delete__(self, instance):
        '''
        USED BY DESCRIPTORS.
        Called to delete an attribute on an instance of the owner class.
        
        @param instance: object
            The instance, None if the owner is the class.
        '''
        assert self._validate(instance)
        self.getProperty().remove(instance)

# --------------------------------------------------------------------

class APICondition:
    '''
    Used to describe methods in criteria that are used by the APIs as queries. The API condition behaves same
    as the API property except the data handling. By convention the descriptor will create in the attributes of 
    the query instance  a variable called '__cond_{descriptor name}_{class field name}' so for the example below 
    the variable will be named '__cond_orderAscending_name'.
    
    ex:
        @APICrtieria()
        class OrderBy:
        
            orderAscending = APICondition(bool)
            
        @APIQuery()
        class Query
            
            name = OrderBy()
            
    @see: APIProperty
    '''
    
    def __init__(self, type):
        '''
        Constructs the API condition descriptor.
        
        @param type: Type|class
            The type of the API condition.
        '''
        self._type = asType(type)
        
    def _initializeInstance(self, byClass, name):
        '''
        TO BE USED ONLY BE SPECIALLY DESIGNED CLASSES.
        Initialize the condition instance by providing the name under which the condition has been declared.
        
        @param name: string
            The name under which the condition has been declared in the query class.
        '''
        assert not hasattr(self, '_condition'), 'Already initialized'
        assert isinstance(name, str), 'Invalid string %s for name' % name
        self._condition = Condition(name, self._type)
        log.debug('Registered condition %s for class %s', self._condition, byClass)
            
    def _validate(self, instance):
        '''
        Internal method used for validating the provided instance.
        '''
        assert isinstance(instance, tuple) and len(instance) == 2, \
        'Invalid tuple %s, needs two elements maybe you forgot to decorate with APICriteria?' % instance
        query, criteria = instance
        assert isinstance(query, Query), \
        'Invalid query %s, maybe you forgot to decorate with APIQuery?' % query
        assert isinstance(criteria, Criteria), \
        'Invalid criteria %s, maybe you forgot to decorate with APICriteria?' % query
        assert self.getCondition() in criteria.getConditions(), \
        'Invalid criteria %s does not contain this %s condition' % (instance, self._condition)
        return True
        
    def getCondition(self):
        '''
        Provides the condition that this descriptor is constructed on.
        
        @return: Condition
            The condition of the descriptor.
        '''
        try: return self._condition
        except AttributeError:
            raise AssertionError('Not initialized %s, maybe you forgot to decorate the criteria with APICriteria?'\
                                  % self)
        
    def __get__(self, instance, owner):
        '''
        USED BY DESCRIPTORS.
        @see: APIProperty.__get__
        
        @param instance: tuple
            The query instance and the criteria instance, None if the owner is the class.
        @param owner: class 
            The owner class.
        '''
        if instance is None:
            raise AssertionError('Invalid operation, only available based on criteria instance call')
        assert self._validate(instance)
        query, criteria = instance
        return self.getCondition().get(criteria, query)
        
    def __set__(self, instance, value):
        '''
        USED BY PYTHON DESCRIPTORS.
        @see: APIProperty.__set__
        
        @param instance: tuple
            The query instance and the criteria instance, None if the owner is the class.
        @param value: object
            The value to set.
        '''
        assert self._validate(instance)
        query, criteria = instance
        self.getCondition().set(criteria, query, value)

    def __delete__(self, instance):
        '''
        USED BY DESCRIPTORS.
        @see: APIProperty.__delete__
        
        @param instance: tuple
            The query instance and the criteria instance, None if the owner is the class.
        '''
        assert self._validate(instance)
        query, criteria = instance
        self.getCondition().remove(criteria, query)

class _CriteriaDescriptorSupport:
        '''
        O BE USED ONLY BE SPECIALLY DESIGNED CLASSES.
        Since also the criteria will be used as a descriptor in the query we need a mechanism for
        combining the query instance with criteria instance.
        '''
        
        def __get__(self, instance, owner):
            '''
            USED BY DESCRIPTORS.
            '''
            if instance is None:
                raise AssertionError('Invalid operation, only available based on query instance call')
            return (instance, self)

        def __set__(self, instance, value):
            '''
            USED BY DESCRIPTORS.
            '''
            raise AssertionError('Invalid operation, cannot modify the criteria')
            
        def __delete__(self, instance):
            '''
            USED BY DESCRIPTORS.
            '''
            raise AssertionError('Invalid operation, cannot remove the criteria')
