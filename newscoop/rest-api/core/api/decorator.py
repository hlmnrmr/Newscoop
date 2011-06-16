'''
Created on Jun 1, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the decorators used for APIs.
'''

from _abcoll import Callable
from functools import wraps
from inspect import getargspec, isfunction
from newscoop.core.api.exception import InputException
from newscoop.core.api.operator import Call, Service, Model, Condition, \
    Criteria, Query
from newscoop.core.api.type import Types, asType
import logging
from newscoop.core.api.descriptor import APIProperty, APICondition, \
    _CriteriaDescriptorSupport

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class APIModel(Callable):
    '''
    Used for decorating classes that are API models.
    
    ex:
        @APIModel()
        class Entity:
    
            name = APIProperty(Integer)
    '''
    
    def __call__(self, originalClass):
        '''
        What happens here is basically that the class that is considered a API model is first
        checked if it has any API properties, if that is the case than it will make a new class
        based on the original one that will also inherit the Model type.
        
        @param originalClass: class
            The original class that contains the API described model methods.
        @return: class
            The new Model enhanced class.
        '''
        properties = []
        for name, prop in originalClass.__dict__.items():
            if isinstance(prop, APIProperty):
                prop._initializeInstance(originalClass, name)
                properties.append(prop.getProperty())
        assert not len(properties) == 0, 'There are no API properties on the provided class %s' % originalClass
    
        newClass = type(originalClass.__name__, (originalClass, Model), {})
        newClass._initialize(properties);
        log.debug('Created model for %s containing %s API properties', newClass, len(properties))
        return newClass

# --------------------------------------------------------------------

class APIQuery(Callable):
    '''
    Used for decorating classes that are API queries.
    
    ex:
        @APIQuery()
        class ThemeQuery:
            
            NAME = OrderBy()
    '''
    
    def __call__(self, originalClass):
        '''
        What happens here is basically that the class that is considered a API query is first
        checked if it has any criteria declared, if that is the case than it will make a new class
        based on the original one that will also inherit the Query type.
        
        @param originalClass: class
            The original class that contains the criteria class attributes.
        @return: class
            The new Query enhanced class.
        '''
        criterias = []
        for name, criteria in originalClass.__dict__.items():
            if isinstance(criteria, Criteria):
                criteria._initializeInstance(name)
                criterias.append(criteria)
        assert not len(criterias) == 0, 'There are is Criteria defined on the provided class %s' % originalClass
    
        newClass = type(originalClass.__name__, (originalClass, Query), {})
        newClass._initialize(criterias);
        log.debug('Created query for %s containing %s API criteria', newClass, len(criterias))
        return newClass
    
class APICriteria(Callable):
    '''
    Used for decorating classes that are API criteria's.
    
    ex:
        @APICriteria()
        class OrderBy:
    
            order = APICondition(bool)
    '''
    
    def __call__(self, originalClass):
        '''
        What happens here is basically that the class that is considered a API criteria is first
        checked if it has any API condition, if that is the case than it will make a new class
        based on the original one that will also inherit the Criteria type.
        
        @param originalClass: class
            The original class that contains the API described condition methods.
        @return: class
            The new Criteria enhanced class.
        '''
        conditions = []
        for name, cond in originalClass.__dict__.items():
            if isinstance(cond, APICondition):
                cond._initializeInstance(originalClass, name)
                conditions.append(cond.getCondition())
        assert not len(conditions) == 0, 'There are no API conditions on the provided class %s' % originalClass
        
        newClass = type(originalClass.__name__, (originalClass, Criteria, _CriteriaDescriptorSupport), {})
        newClass._initialize(conditions);
        log.debug('Created criteria for %s containing %s API conditions', newClass, len(conditions))
        return newClass
    
# --------------------------------------------------------------------

class APIService(Callable):
    '''
    Used for decorating classes that are API services.
    
    ex:
        @APIService()
        class IEntityService:
    
            @call(Number, Number)
            def multipy(self, x):
    '''
    
    def __call__(self, originalClass):
        '''
        What happens here is basically that the class that is considered a API service is first
        checked if it has any API calls, if that is the case than it will make a new class
        based on the original one that will also inherit the Service operator.
        
        @param originalClass: class
            The original class that contains the API described service methods.
        @return: class
            The new Service enhanced class.
        '''
        calls = []
        for func in originalClass.__dict__.values():
            if isfunction(func):
                try:
                    calls.append(func._call)
                except AttributeError:
                    log.warn('Function %s is not an API call, maybe you forgot to decorated with APICall?', func)
        assert not len(calls) == 0, 'There are no API calls on the provided class %s' % originalClass
    
        newClass = type(originalClass.__name__, (originalClass, Service), {})
        newClass._initialize(calls);
        log.debug('Created service for %s containing %s API calls', newClass, len(calls))
        return newClass

class APICall(Callable):
    '''
    Used for decorating service methods that are used as APIs.
    When constructing the API service you have to specify the type
    of expected input value and the type of the output values.
    In the example below x value has to be a Number and the return
    value is None. Each call of the APICall methods will delegate
    to the API service implementation. The input types can be also
    function reference from model. 
    
    ex:
        @APICall(None, int)
        def updateX(self, x):
            doc string
            <no method body required>
            
        @APICall(Entity, Entity.x, String)
        def findBy(self, x, name):
            doc string
            <no method body required>
    '''

    def __init__(self, output, *input):
        '''
        Constructs the API call decorator.

        @param output: Type
            The output types expected for the service call.
        @param input: sequence|Type
            The input types expected for the service call.
        '''
        self._outputType = Types(output)
        self._inputTypes = Types(input)
        
    def __call__(self, function):
        '''
        Constructs an API call that will have the provided input and output types. It will also provide a function
        that can be used for calling the service. The service call will be available only after a implementation
        is properly registered.
            
            @param function: FunctionType
                The function that performs the service.
        '''
        assert isfunction(function), 'Invalid function %s' % function
    
        if __debug__:
            fnArgs = getargspec(function)
            assert 'self' == fnArgs.args[0], 'The call needs to be tagged in a class definition'
            assert len(fnArgs.args) == len(self._inputTypes) + 1, \
            'The functions parameters are not equal with the provided input types'
            assert fnArgs.varargs == None, 'No variable arguments are allowed'
            assert fnArgs.keywords == None, 'No keywords arguments are allowed'
            assert fnArgs.defaults == None, 'No default arguments are allowed'
               
        call = Call(function.__name__, self._outputType, self._inputTypes)
        @wraps(function)
        def callWrapper(service, *args):
            '''
            Used for wrapping the actual service function call.
            '''
            assert isinstance(service, Service), \
            'Invalid service %s, maybe you forgot to decorate with APIService?' % service
            assert call in service.getCalls(), 'Invalid service %s does not contain this % call' % (service, call)
            return call.call(service.getImplementation(), args)
        
        callWrapper._call = call
        log.debug('Created, service call for %s with %s inputs and %s as output',
                  function, len(call._inputTypes), call._outputType.__class__.__name__);
        return callWrapper

# --------------------------------------------------------------------
