'''
Created on May 29, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the containers that describe the APIs.
'''

from _abcoll import Iterable
from inspect import ismodule, getargspec
from newscoop.core.api.exception import InputException, OutputException
from newscoop.core.api.type import Type, Types, TypeHolder, TypeForClass
import logging


# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Model(TypeHolder):
    '''
    Used for mapping the API models.
    '''
    
    @classmethod
    def getProperties(cls):
        '''
        Provides the properties of this model class.
        
        @return: tuple
            The list containing the properties of the model.
        '''
        
        try: return cls._properties
        except AttributeError: 
            raise AssertionError('Not initialized %s, maybe you forgot to decorate the model with APIModel?' % cls)
    
    @classmethod
    def getType(cls):
        '''
        @see: TypeHolder.getType
        '''
        try: return cls._type
        except AttributeError: 
            raise AssertionError('Not initialized %s, maybe you forgot to decorate the model with APIModel?' % cls)
    
    @classmethod
    def _initialize(cls, properties):
        '''
        TO BE USED ONLY BE SPECIALLY DESIGNED CLASSES.
        Initialize the properties of this model class.
        
        @param properties: Iterable
            The properties list that belong to this model class.
        '''
        
        assert cls != Model, 'The Model needs to be extended, you cannot add properties directly to the Model'
        assert isinstance(properties, Iterable), 'The properties %s need to be a iterable' % properties
        if __debug__:
            for prop in properties : assert isinstance(prop, Property), 'Not a Property type for %s' % prop
        cls._properties = tuple(properties)
        cls._type = TypeForClass(cls)

class Property:
    '''
    Provides the container for the API property types. It contains the operation that need to be
    applied on a model instance that relate to this property.
    '''

    def __init__(self, name, type):
        '''
        Constructs a property operations container.
        
        @param name: string
            The name of the property as it should be called by.
        @param type: Type
            The Type of the property.
        '''
        assert isinstance(name, str) and str != '', 'Provide a valid name'
        assert isinstance(type, Type), 'Invalid type %s' % type
        self._type = type
        self._name = name
        # Prefixes the name of the fields that are placed in the model automatically.
        self._var = '__prop_' + name
        
    def getName(self):
        '''
        Provides the name of the property.
        
        @return: string
            The name of the property.
        '''
        return self._name
    
    def getType(self):
        '''
        Provides the type of the property.
        
        @return: Type
            The type of the property.
        '''
        return self._type
    
    def get(self, model):
        '''
        Provides the value represented by this property for the provided instance.
        
        @param model: object
            The model instance to provide the value for.
        '''
        assert not model is None, 'Invalid model object (None)'
        return getattr(model, self._var, None)
    
    def set(self, model, value):
        '''
        Set the value represented by this property for the provided model instance.
        
        @param model: object
            The model instance to set the value to.
        @param value: object
            The value to set, needs to be valid for this property.
        '''
        assert not model is None, 'Invalid model object (None)'
        if not value is None and not self._type.isValid(value):
            raise InputException('The property $1 takes a parameter of type $2, illegal value type $3',
                                 self._name, self._type._typeClass, value.__class__.__name__)
        setattr(model, self._var, value)
    
    def remove(self, model):
        '''
        Remove the value represented by this property from the provided model instance.
        
        @param model: object
            The model instance to remove the value from.
         '''
        assert not model is None, 'Invalid model object (None)'
        delattr(model, self._var)

    def __str__(self):
        return '<Property[%s = %s]>' % (self._name, self._type)
        
# --------------------------------------------------------------------

class Query:
    '''
    Used for mapping the API query.
    '''
    
    @classmethod
    def getCriterias(cls):
        '''
        Provides the criteria's of this query class.
        
        @return: tuple
            The tuple containing the criteria's of the query.
        '''
        try: return cls._criterias
        except AttributeError: 
            raise AssertionError('Not initialized %s, maybe you forgot to decorate the query with APIQuery?' \
                                 % cls)
    
    @classmethod
    def _initialize(cls, criterias):
        '''
        TO BE USED ONLY BE SPECIALLY DESIGNED CLASSES.
        Initialize the criteria's of this query class.
        
        @param criterias: Iterable
            The criteria's list that belong to this query class.
        '''
        assert cls != Query, \
        'The Query needs to be extended, you cannot add criteria directly to the Query'
        assert isinstance(criterias, Iterable), 'The criteria %s need to be a iterable' % criterias
        assert all([isinstance(crt, Criteria) for crt in criterias]), 'Not a Criteria type for %s' % crt
        cls._criterias = tuple(criterias)
    
class Criteria:
    '''
    Used for mapping the API criteria.
    '''
    
    @classmethod
    def getConditions(cls):
        '''
        Provides the conditions of this criteria class.
        
        @return: tuple
            The list containing the properties of the model.
        '''
        try: return cls._conditions
        except AttributeError: 
            raise AssertionError('Not initialized %s, maybe you forgot to decorate the criteria with APICriteria?' \
                                 % cls)
    
    @classmethod
    def _initialize(cls, conditions):
        '''
        TO BE USED ONLY BE SPECIALLY DESIGNED CLASSES.
        Initialize the conditions of this criteria class.
        
        @param conditions: Iterable
            The conditions list that belong to this criteria class.
        '''
        assert cls != Criteria, \
        'The Criteria needs to be extended, you cannot add conditions directly to the Criteria'
        assert isinstance(conditions, Iterable), 'The conditions %s need to be a iterable' % conditions
        assert all([isinstance(cond, Condition) for cond in conditions]), 'Not a Condition type for %s' % cond
        cls._conditions = tuple(conditions)
        
    def _initializeInstance(self, name):
        '''
        TO BE USED ONLY BE SPECIALLY DESIGNED CLASSES.
        Initialize the criteria instance by providing the name under which the criteria has been declared.
        
        @param name: string
            The name under which the criteria has been declared in the query class.
        '''
        assert not hasattr(self, '_name'), 'Already initialized'
        assert isinstance(name, str), 'Invalid string for name %s ' % name
        self._name = name

    def getName(self):
        '''
        Provides the name for this criteria instance.
        
        @return: string
            The criteria name.
        '''
        try: return self._name
        except AttributeError: 
            raise AssertionError('Not initialized %s, maybe you forgot to decorate the query with APIQuery?' % self)
        
class Condition:
    '''
    Provides the container for the API condition types. It contains the operation that need to be
    applied on a query instance that relate to this condition.
    '''

    def __init__(self, name, type):
        '''
        Constructs a condition operations container.
        
        @param name: string
            The name of the condition as it should be called by.
        @param type: Type
            The Type of the condition.
        '''
        assert isinstance(name, str) and str != '', 'Provide a valid name'
        assert isinstance(type, Type), 'Invalid type %s' % type
        self._type = type
        self._name = name
        # Prefixes the name of the fields that are placed in the query automatically.
        self._var = '__cond_' + name + '_'
    
    def get(self, criteria, query):
        '''
        Provides the value represented by this condition for the provided instance.
        
        @param criteria: Criteria
            The criteria instance that contains this condition.
        @param query: object
            The query instance to provide the value for.
        '''
        assert isinstance(criteria, Criteria), 'Invalid criteria %s' % criteria
        assert not query is None, 'Invalid query object (None)'
        return getattr(query, self._var + criteria.getName(), None)
    
    def set(self, criteria, query, value):
        '''
        Set the value represented by this condition for the provided query instance.
        
        @param criteria: Criteria
            The criteria instance that contains this condition.
        @param query: object
            The query instance to set the value to.
        @param value: object
            The value to set, needs to be valid for this condition.
        '''
        assert isinstance(criteria, Criteria), 'Invalid criteria %s' % criteria
        assert not query is None, 'Invalid query object (None)'
        if not value is None and not self._type.isValid(value):
            raise InputException('The condition $1 takes a parameter of type $2, illegal value type $3',
                                 self._name, self._type._typeClass, value.__class__.__name__)
        setattr(query, self._var + criteria.getName(), value)
        return value
    
    def remove(self, criteria, query):
        '''
        Remove the value represented by this condition from the provided query instance.
        
        @param criteria: Criteria
            The criteria instance that contains this condition.
        @param query: object
            The query instance to remove the value from.
         '''
        assert isinstance(criteria, Criteria), 'Invalid criteria %s' % criteria
        assert not query is None, 'Invalid model object (None)'
        delattr(query, self._var + criteria.getName())
    
    def __str__(self):
        return '<Condition[%s = %s]>' % (self._name, self._type)
    
# --------------------------------------------------------------------

class Call:
    '''
    Provides the container for a service call. This class will basically contain all the
    Property types that are involved in input and output from the call.
    '''
    
    def __init__(self, name, outputType, inputTypes):
        '''
        Constructs an API call that will have the provided input and output types.
        
        @param name: string
            The name of the function that will be called on the service implementation.
        @param outputType: Type
            The output type for the service call.
        @param inputTypes: Types
            The input types for the service call.
        '''
        assert isinstance(name, str) and str != '', 'Provide a valid name'
        assert isinstance(outputType, Type), 'Invalid output Type %s' % outputType
        assert isinstance(inputTypes, Types), 'Invalid input Types %s' % inputTypes
        self._name = name
        self._outputType = outputType
        self._inputTypes = inputTypes
    
    def isCallable(self, impl):
        '''
        Checks if the provided implementation class contains the required function
        to be called by this call container.
        
        @param impl: class|module
            Either the instance or module that implements the API service method.
        '''
        if ismodule(impl):
            func = self._findModuleFunction(impl)
        else:
            func = self._findClassFunction(impl.__class__)
        return not func is None
        
    def call(self, impl, args):
        '''
        Performs the check of the input and output parameters for a service call
        and calls the representative method from the provided implementation.
        
        @param impl: object
            The implementation that reflects the service call that is
            contained by this call.
        @param args: tuple
            The arguments to be used in invoking the service 
        '''
        assert not impl is None, 'Provide the service implementation to be used foe calling the represented function'
        assert isinstance(args, tuple), 'The arguments %s need to be a tuple' % args
        
        if not self._inputTypes.isValid(args):
            raise InputException('The arguments $1 provided are not compatible with the expected input $2',
                                 args, self._inputTypes)
        
        if ismodule(impl):
            func = self._findModuleFunction(impl)
            assert not func is None, \
            'Could not locate any function to call on the provided service module implementation'
            ret = func.__call__(*args)
        else:
            func = self._findClassFunction(impl.__class__)
            assert not func is None, \
            'Could not locate any function to call on the provided service class implementation'
            ret = func.__call__(impl, *args)
            
        if not self._outputType.isValid(ret):
            raise OutputException('The return ($1) provided is not compatible with the expected output $2',
                                 ret, self._outputType)
        
        log.debug('Success calling %s with arguments %s and return %s', func, args, ret)
        return ret
    
    def _findClassFunction(self, implClass):
        '''
        Finds the class function that is represented by this call.
        
        @return: function|None
            Returns the function if found for the provided class or None
            if no such function could be located.
        '''
        func = getattr(implClass, self._name, None)
        if not func is None:
            fnArgs = getargspec(func)
            if len(fnArgs.args) == len(self._inputTypes) + 1:
                return func
                        
    def _findModuleFunction(self, implModule):
        '''
        Finds the module function that is represented by this call.
        
        @return: function|None
            Returns the function if found for the provided module or None
            if no such function could be located.
        '''
        func = getattr(implModule, self._name, None)
        if not func is None:
            fnArgs = getargspec(func)
            if len(fnArgs.args) == len(self._inputTypes):
                return func

    def __str__(self):
        return '<Call[%s %s(%s)]>' % (self._outputType, self._name, self._inputTypes)

class Service:
    '''
    Used for mapping the API calls.
    '''
    
    @classmethod
    def getCalls(cls):
        '''
        Provides the calls of this service class.
        
        @return: tuple
            The list containing the calls of the service.
        '''
        try: return cls._calls
        except AttributeError: 
            raise AssertionError('Not initialized %s, maybe you forgot to decorate the service with APIService?'\
                                  % cls)
    
    @classmethod
    def _initialize(cls, calls):
        '''
        TO BE USED ONLY BE SPECIALLY DESIGNED CLASSES.
        Initialize the calls of this service class.
        
        @param calls: Iterable
            The calls list that belong to this service class.
        '''
        assert cls != Service, 'The Service needs to be extended, you cannot add calls directly to the Service'
        assert isinstance(calls, Iterable), 'The calls %s need to be a iterable' % calls
        assert all([isinstance(call, Call) for call in calls]), 'Not a Call type for %s' % call
        cls._calls = tuple(calls)
        
    def __init__(self, impl):
        '''
        Constructs the API service class based on the provided implementation.
        
        @param impl: object
            An instance of the class that implements all the methods required by the
            service.
        '''
        assert not impl is None, 'Invalid implementation (None)'
        if __debug__:
            for call in self.getCalls():
                assert call.isCallable(impl), 'The provided implementation %s is not suited for %s' % (impl, call)
        self._impl = impl
        
    def getImplementation(self):
        '''
        Provides the implementation class assigned to this service instance.
        
        @return: object
            The implementation assigned.
        '''
        return self._impl
