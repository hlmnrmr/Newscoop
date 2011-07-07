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
from inspect import getargspec, isfunction, isclass
from ally.core.api.operator import Call, Service, Criteria, Query, Model, \
    Property, CriteriaEntry, Properties
from ally.core.api.type import TypeProperty, typeFor, TypeModel, List, Type, \
    TypeQuery, Iter, Input
from ally.core.util import fullyQName, guard
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@guard(ifNoneSet='name')
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

    def __init__(self, type, name=None):
        '''
        Constructs the API property descriptor.
        
        @param type: Type|class
            The type of the API property.
        @param name: string
            The name that this property has been declared on, needs to be provided by the class decorator, either
            APIModel or APICriteria.
        @ivar _typesByClass: 
            Contains cached types based on model classes.
        '''
        self.type = typeFor(type)
        self.name = name
        self._typesByClass = {}
    
    def _getProperties(self, owner):
        properties = propertiesFor(owner)
        assert isinstance(properties, Properties), \
        'Invalid owner class %s, is not associated with any properties' % owner
        return properties
    
    def _getProperty(self, owner, properties=None):
        properties = properties or self._getProperties(owner)
        assert isinstance(properties, Properties)
        assert self.name in properties.properties, \
        'Invalid properties %s has no property for name <%s>' % (properties, self.name)
        return properties.properties[self.name]

    def __get__(self, instance, owner):
        '''
        USED BY DESCRIPTORS.
        '''
        properties = self._getProperties(owner)
        prop = self._getProperty(owner, properties)
        assert isinstance(prop, Property)
        if instance is None:
            name = fullyQName(owner)
            if not name in self._typesByClass:
                self._typesByClass[name] = TypeProperty(properties, prop)
                log.info('Created type for property %s for class %s', prop, owner)
            return self._typesByClass[name]
        return prop.get(instance)
        
    def __set__(self, instance, value):
        '''
        USED BY PYTHON DESCRIPTORS.
        '''
        prop = self._getProperty(instance.__class__)
        assert isinstance(prop, Property)
        prop.set(instance, value)

    def __delete__(self, instance):
        '''
        USED BY DESCRIPTORS.
        '''
        prop = self._getProperty(instance.__class__)
        assert isinstance(prop, Property)
        prop.remove(instance)

# --------------------------------------------------------------------

@guard
class APIModel(Callable):
    '''
    Used for decorating classes that are API models.
    
    ex:
        @APIModel()
        class Entity:
    
            name = APIProperty(Integer)
    '''
    
    def __call__(self, modelClass):
        '''
        What happens here is basically that the class that is considered an API model is first
        checked if it has any API properties, if that is the case than it will associate a model to this model class.
        
        @param modelClass: class
            The model class to be processed.
        @return: class
            The same model class.
        '''
        properties = _processAPIProperties(modelClass)
        model = propertiesFor(modelClass)
        if model is None:
            # this is not an extended model
            assert not len(properties) == 0, 'There are no API properties on model class %s' % modelClass
            model = Model(modelClass, properties)
        else:
            assert isinstance(model, Model)
            allProperties = dict(model.properties)
            allProperties.update(properties)
            model = Model(modelClass, allProperties)
        propertiesFor(modelClass, model)
        typeFor(modelClass, TypeModel(model))
        log.info('Created model %s for class %s containing %s API properties', model, modelClass, len(properties))
        return modelClass
        
# --------------------------------------------------------------------

# Whenever the set is called on the criteria descriptor than this condition property will be used.
DEFAULT_CONDITIONS = []

@guard(ifNoneSet='name')
class APIEntry():
    '''
    Since the criteria will be used as a descriptor in the query we need a mechanism for combining the query 
    instance with criteria instance. What this descriptor will do is when a criteria is required it will
    construct a criteria model class instance that will be used for populating the property conditions.
    '__prop_{criteria name}' so for the example below the variable will be named '__prop_name'.
    
    ex:
        @APIQuery()
        class Query:
        
            name = APIEntry(OrderBy)
    '''

    def __init__(self, criteriaClass, name=None):
        '''
        Constructs the API entry descriptor.
        
        @param criteriaClass: class
            The criteria class represented by this entry.
        @param name: string
            The name that this entry has been declared on, needs to be provided by the class decorator APIQuery
        '''
        assert isinstance(propertiesFor(criteriaClass), Criteria), 'Invalid criteria class %s' % criteriaClass
        self.criteriaClass = criteriaClass
        self.name = name
    
    def _getQuery(self, instance):
        query = queryFor(instance)
        assert isinstance(query, Query), 'Invalid instance %, is not associated with a query' % instance
        return query
    
    def _getCriteriaEntry(self, instance, query=None):
        query = query or self._getQuery(instance)
        assert self.name in query.criteriaEntries, \
        'Invalid query %s has no criteria for name <%s>' % (query, self.name)
        return query.criteriaEntries[self.name]

    def _obtainActive(self, instance, query=None, crtEntry=None):
        '''
        Provides the active criteria that reflects this criteria descriptor.
        
        @param instance: object
            The query to get the active criteria for.
        @return: Criteria
            The active criteria or the new created active criteria.
        '''
        query = query or self._getQuery(instance)
        crtEntry = crtEntry or self._getCriteriaEntry(instance, query)
        assert isinstance(crtEntry, CriteriaEntry)
        return crtEntry.obtain(instance)
    
    def __get__(self, instance, owner):
        '''
        USED BY DESCRIPTORS.
        '''
        if instance is None:
            raise AssertionError('Invalid operation, only available based on query instance call')
        return self._obtainActive(instance)
        
    def __set__(self, instance, value):
        '''
        USED BY DESCRIPTORS.
        '''
        query = self._getQuery(instance)
        crtEntry = self._getCriteriaEntry(instance, query)
        assert isinstance(crtEntry, CriteriaEntry)
        active = self._obtainActive(instance, query, crtEntry)
        criterias = crtEntry.criteria
        for cond in DEFAULT_CONDITIONS:
            if cond in criterias:
                crt = criterias[cond]
                assert isinstance(crt, Property)
                crt.set(active, value)
                return
        raise AssertionError('No default conditions %s found in criteria %s' % (DEFAULT_CONDITIONS, active))
        
    def __delete__(self, instance):
        '''
        USED BY DESCRIPTORS.
        '''
        crtEntry = self._getCriteriaEntry(instance)
        assert isinstance(crtEntry, CriteriaEntry)
        crtEntry.remove(instance)

@guard    
class APIQuery(Callable):
    '''
    Used for decorating classes that are API queries.
    
    ex:
        @APIQuery(ThemeModel)
        class ThemeQuery:
            
            name = OrderBy
    '''
    
    def __init__(self, modelClass):
        '''
        Creates the query instance based on the provided model class.
        
        @param modelClass: class
            The class of the model that this query represents.
        '''
        assert isinstance(propertiesFor(modelClass), Model), 'Invalid model class %s' % modelClass
        self.modelClass = modelClass
    
    def __call__(self, queryClass):
        '''
        What happens here is basically that the class that is considered a API query is first
        checked if it has any entries declared, if that is the case than it associated a query to this class.
        
        @param queryClass: class
            The query class that contains the criteria class attributes.
        @return: class
            The query class processed.
        '''
        model = propertiesFor(self.modelClass)
        assert isinstance(model, Model), 'Invalid model class %s' % self.modelClass
        assert model.query is None, 'Illegal model %s it has a query' % model
        entries = _processAPIEntries(queryClass)
        query = queryFor(queryClass)
        if query is None:
            # this is not an extended query
            query = Query(queryClass, entries)
        else:
            assert isinstance(query, Query)
            allEntries = dict(query.criteriaEntries)
            allEntries.update(entries)
            query = Query(queryClass, allEntries)
        queryFor(queryClass, query)
        typeFor(queryClass, TypeQuery(query))
        model.query = query
        log.info('Created query %s for class %s containing %s API entries', query, queryClass, len(entries))
        return queryClass
    
# --------------------------------------------------------------------

@guard
class APICriteria(Callable):
    '''
    Used for decorating classes that are API criteria's.
    Attention the declared criteria will have the __new__ redeclared in order to provide the criteria descriptor
    instead of the actual criteria, so do not create criteria instance only when is in the purpose of creating
    a query.
    Each decorated criteria instance will contain the fields 'query' containing the query that owns the criteria
    and 'entryName' the name under which the criteria has been declared.
    
    ex:
        @APICriteria()
        class OrderBy:
    
            order = APIProperty(bool)
    '''
    
    def __call__(self, criteriaClass):
        '''
        What happens here is basically that the class that is considered an API criteria is first
        checked if it has any API properties, if that is the case than it will associate a criteria to this
        criteria class.
        
        @param criteriaClass: class
            The criteria class to be processed.
        @return: class
            The criteria class processed.
        '''
        properties = _processAPIProperties(criteriaClass)
        criteria = propertiesFor(criteriaClass)
        if criteria is None:
            # this is not an extended criteria
            assert not len(properties) == 0, 'There are no API properties on criteria class %s' % criteriaClass
            criteria = Criteria(criteriaClass, properties)
        else:
            assert isinstance(criteria, Criteria)
            allProperties = dict(criteria.properties)
            allProperties.update(properties)
            criteria = Criteria(criteriaClass, allProperties)
        propertiesFor(criteriaClass, criteria)
        log.info('Created criteria %s for class %s containing %s API conditions', criteria,
                 criteriaClass, len(properties))
        return criteriaClass
    
# --------------------------------------------------------------------

@guard
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
        @param input: tuple
            The input types expected for the service call.
        @ivar inputTypes: list
            The Types obtained from the provided input.
        @ivar name: string
            The name of the call, it will be assigned when the decorator call is made.
        @ivar mandatoryCount: integer
            Provides the count of the mandatory input types, if the mandatory count is two and we have three input
            types it means that just the first two parameters need to be provided, at initialization the mandatory
            count is equal with the input count. It will be adjusted on the decorator call.
        '''
        self.outputType = typeFor(output)
        assert isinstance(input, tuple), 'Invalid input %s it needs to be a tuple' % input
        self.inputTypes = []
        for type in input:
            typ = typeFor(type)
            assert isinstance(typ, Type), 'Could not obtain a valid Type for %s' % type
            self.inputTypes.append(typ)
        self.name = None
        self.mandatoryCount = len(self.inputTypes)

    def __call__(self, function):
        '''
        Constructs an API call that will have the provided input and output types. It will also provide a function
        that can be used for calling the service. The service call will be available only after a implementation
        is properly registered.
            
            @param function: FunctionType
                The function that performs the service.
        '''
        assert isfunction(function), 'Invalid function %s' % function
        fnArgs = getargspec(function)
        assert 'self' == fnArgs.args[0], 'The call needs to be tagged in a class definition'
        assert len(fnArgs.args) == 1 + len(self.inputTypes), \
        'The functions parameters are not equal with the provided input types'
        assert fnArgs.varargs is None, 'No variable arguments are allowed'
        assert fnArgs.keywords is None, 'No keywords arguments are allowed'
        if fnArgs.defaults is not None:
            self.mandatoryCount -= len(fnArgs.defaults)
        self.name = function.__name__
        self.inputs = [Input(name, typ) for name, typ in zip(fnArgs.args[1:], self.inputTypes)]
        @wraps(function)
        def callFunction(srv, *args):
            '''
            Used for wrapping the actual service function call.
            '''
            assert isinstance(srv, ServiceSupport), \
            'Invalid service %s, maybe you forgot to decorate with APIService?' % srv
            service = serviceFor(srv)
            assert isinstance(service, Service), 'Invalid service instance for %s' % srv
            assert self.name in service.calls, \
            'Invalid service %s has no call for name <%s>' % (service, self.name)
            return service.calls[self.name].call(srv.implementation, args)
        callFunction.APICall = self
        return callFunction

@guard
class APIService(Callable):
    '''
    Used for decorating classes that are API services.
    
    ex:
        @APIService(Entity)
        class IEntityService:
    
            @call(Number, Entity.x)
            def multipy(self, x):
    '''
    
    def __init__(self, modelClass):
        '''
        Creates the service instance based on the provided model class.
        
        @param modelClass: class
            The class of the model that this service represents.
        '''
        assert isinstance(propertiesFor(modelClass), Model), 'Invalid model class %s' % modelClass
        self.modelClass = modelClass
    
    def __call__(self, serviceClass):
        '''
        What happens here is basically that the class that is considered a API service is first
        checked if it has any API calls, if that is the case it will associate a service to this service class.
        
        @param originalClass: class
            The original class that contains the API described service methods.
        @return: class
            The extended service class if is the case, the service class is forced to extend the Service support.
        '''
        calls = _processAPICalls(serviceClass)
        parentServices = (serviceFor(parent) for parent in serviceClass.__bases__)
        parentServices = [service for service in parentServices if service is not None] 
        if len(parentServices) == 0:
            # this is not an extended service
            assert not len(calls) == 0, 'There are no API calls on service class %s' % calls
            service = Service(propertiesFor(self.modelClass), serviceClass, calls)
        else:
            allCalls = {}
            for parent in parentServices:
                assert isinstance(parent, Service)
                model = propertiesFor(self.modelClass)
                assert isinstance(model, Model), 'Invalid model %s' % model
                if self.modelClass is not parent.model.modelClass \
                and issubclass(self.modelClass, parent.model.modelClass):
                    log.info('Detected generic inheritance from model %s to model %s', \
                             parent.model.modelClass, self.modelClass)
                    for name, call in parent.calls.items():
                        if name not in calls:
                            allCalls[name] = _processCallGeneric(call, parent.model, model)
                        else:
                            allCalls[name] = call
                else:
                    allCalls.update(parent.calls)
            allCalls.update(calls)
            service = Service(model, serviceClass, allCalls)
        serviceFor(serviceClass, service)
        if not isinstance(serviceClass, ServiceSupport):
            newServiceClass = type(serviceClass.__name__, (serviceClass, ServiceSupport), {})
            newServiceClass.__module__ = serviceClass.__module__
            serviceClass = newServiceClass
        log.info('Created service %s for class %s ', service, serviceClass)
        return serviceClass

# --------------------------------------------------------------------

@guard
class ServiceSupport:
    '''
    Provides support for service. Basically all API services should extend this interface, or can be forced to do
    that by the APIService. This class will provide access to an implementation of the service. 
    '''
    
    def __init__(self, implementation):
        '''
        Constructs the API service class based on the provided implementation.
        
        @param implementation: object
            An instance of the class that implements all the methods required by the
            service.
        @ivar service: Service
            The service class associated with the support.
        '''
        assert not implementation is None, 'Invalid implementation (None)'
        service = serviceFor(self)
        assert isinstance(service, Service), \
        'Cannot obtain an associated service for %s, maybe you are not using right this class' % self
        if __debug__:
            for call in service.calls.values():
                assert call.isCallable(implementation), \
                'The provided implementation %s is not suited for %s' % (implementation, call)
        self.implementation = implementation

# --------------------------------------------------------------------

# A list of names to be ignored when searching for properties or criteria
_IGNORE_NAMES = ['__dict__', '__module__', '__weakref__', '__doc__']

def _processAPIProperties(propertiesClass):
    '''
    ONLY FOR INTERNAL USE.
    Processes the API properties in the properties model class.
    
    @param propertiesClass: class
        The properties class.
    @return: dictionary
        A dictionary containing as a key the property name and as a value the property.
    '''
    log.info('Processing properties for %s', propertiesClass)
    properties = {}
    for name, value in propertiesClass.__dict__.items():
        if name in _IGNORE_NAMES or isfunction(value):
            continue
        apiProp = None
        if isinstance(value, APIProperty):
            apiProp = value
            apiProp.name = name
            log.info('Found property for <%s> of type %s', name, apiProp.type)
        else:
            type = typeFor(value)
            if type is not None:
                apiProp = APIProperty(type, name)
                setattr(propertiesClass, name, apiProp)
                log.info('Created property based on found type %s for <%s>', type, name)
        if apiProp is not None:
            properties[name] = Property(name, apiProp.type)
        else:
            log.warning('Cannot process property for class %s field <%s> of value %s', propertiesClass, name, value)
    return properties

def _processAPIEntries(queryClass):
    '''
    ONLY FOR INTERNAL USE.
    Processes the API entries in the provided query class.
    
    @param queryClass: class
        The query class.
    @return: dictionary
        A dictionary containing as a key the entry name and as a value the entry.
    '''
    log.info('Processing entries for query %s', queryClass)
    entries = {}
    for name, value in queryClass.__dict__.items():
        if name in _IGNORE_NAMES or isfunction(value):
            continue
        crtEntr = None
        if isinstance(value, APIEntry):
            criteria = propertiesFor(value.criteriaClass)
            assert isinstance(criteria, Criteria), 'Invalid APIEntry criteria class %s' % value.criteriaClass
            value.name = name
            crtEntr = CriteriaEntry(criteria, name)
            log.info('Found entry for <%s> of criteria %s', name, criteria)
        if not isclass(value):
            value = value.__class__
        criteria = propertiesFor(value)
        if isinstance(criteria, Criteria):
            crtEntr = CriteriaEntry(criteria, name)
            apiEntr = APIEntry(value, name)
            setattr(queryClass, name, apiEntr)
            log.info('Created entry based on found criteria %s class for <%s>', criteria, name)
        if crtEntr is not None:
            entries[name] = crtEntr
        else:
            log.warning('Cannot process entry for class %s field <%s> of value %s', queryClass, name, value)
    return entries

def _processAPICalls(serviceClass):
    '''
    ONLY FOR INTERNAL USE.
    Processes the API calls in the provided service class.
    
    @param serviceClass: class 
        The service class to search the calls for.
    @return: dictionary
        A dictionary containing all the Call's attached to the API calls found, as key is the name of the 
        API call decorated function.
    '''
    log.info('Processing calls for %s', serviceClass)
    calls = {}
    for name, func in serviceClass.__dict__.items():
        if isfunction(func):
            apiCall = None
            try:
                apiCall = func.APICall
                assert isinstance(apiCall, APICall), 'Expected API call %' % apiCall
                call = Call(name, apiCall.outputType, apiCall.inputs, apiCall.mandatoryCount)
                calls[name] = call
                log.info('Found call %s', call)
            except AttributeError:
                log.warn('Function %s is not an API call, maybe you forgot to decorated with APICall?', \
                         func.__name__)
    return calls

def _processCallGeneric(call, superModel, newModel):
    '''
    ONLY FOR INTERNAL USE.
    Processes the provided call if is the case to a extended call based on the model class.
    If either the output or input is based on the provided super model than it will create new call that will have
    the super model replaced with the new model in the types of the call.
    
    @param call: Call
        The call to be analyzed.
    @param superModel: Model
        The super model, usually this is the model that might be found in the call.
    @param newModel: Model
        The new model to be used in creating the new generic call.
    @return: Call
        If the provided call is not depended on the super model it will be returned as it is, if not a new call
        will be created with all the dependencies from super model replaced with the new model.
    '''
    assert isinstance(call, Call)
    assert isinstance(newModel, Model)
    updated = False
    outputType = _processTypeGeneric(call.outputType, superModel, newModel)
    if outputType is not None:
        updated = True
    else:
        outputType = call.outputType
    inputs = []
    for input in call.inputs:
        assert isinstance(input, Input)
        genericType = _processTypeGeneric(input.type, superModel, newModel)
        if genericType is not None:
            inputs.append(Input(input.name, genericType))
            updated = True
        else:
            inputs.append(input)
    if updated:
        newCall = Call(call.name, outputType, inputs, call.mandatoryCount)
        log.info('Generic call transformation from %s to %s' % (call, newCall))
        call = newCall
    return call

def _processTypeGeneric(typ, superModel, newModel):
    '''
    ONLY FOR INTERNAL USE.
    Processes the type if is the case into a new type that is extended from the original but having the new
    model as reference instead of the super model.
    @see: _processCallGeneric
    
    @param typ: Type
        The type to process.
    @param superModel: Model
        The model to check for and replace with new model.
    @param newModel: Model
        The new model to be used.
    @return: Type|None
        If the provided type was containing references to the super model than it will return a new type
        with the super model references changes to the new model, otherwise returns None.
    '''
    newType = None
    if isinstance(typ, TypeProperty):
        assert isinstance(typ, TypeProperty)
        if typ.model is superModel:
            newType = TypeProperty(newModel, typ.property)
    elif isinstance(typ, TypeModel):
        assert isinstance(typ, TypeModel)
        if typ.model is superModel:
            newType = TypeModel(newModel)
    elif isinstance(typ, TypeQuery):
        assert isinstance(typ, TypeQuery)
        if typ.query is superModel.query and newModel.query is not None:
            newType = TypeQuery(newModel.query)
    elif isinstance(typ, List):
        assert isinstance(typ, List)
        newType = List(_processTypeGeneric(typ.itemType, superModel, newModel))
    elif isinstance(typ, Iter):
        assert isinstance(typ, Iter)
        newType = Iter(_processTypeGeneric(typ.itemType, superModel, newModel))
    return newType

# --------------------------------------------------------------------

def propertiesFor(obj, properties=None):
    '''
    If the model is provided it will be associate with the obj, if the model is not provided than this function
    will try to provide if it exists the model associated with the obj.
    
    @param obj: object|class
        The class to associate or extract the model.
    @param properties: Properties
        The properties to associate with the obj.
    @return: Properties|None
        If the properties has been associate then the return will be none, if the properties is being extracted it 
        can return either the Properties or None if is not found.
    '''
    if properties is None:
        return getattr(obj, 'api_properties', None)
    assert isinstance(properties, Properties), 'Invalid properties %s' % properties
    assert 'api_properties' not in obj.__dict__, 'Already has a properties %s' % obj
    setattr(obj, 'api_properties', properties)

def queryFor(obj, query=None):
    '''
    If the query is provided it will be associate with the obj, if the query is not provided than this function
    will try to provide if it exists the query associated with the obj.
    
    @param obj: object|class
        The class to associate or extract the query.
    @param query: Query
        The Query to associate with the obj.
    @return: Query|None
        If the query has been associate then the return will be none, if the query is being extracted it can
        return either the Query or None if is not found.
    '''
    if query is None:
        return getattr(obj, 'api_query', None)
    assert isinstance(query, Query), 'Invalid query %s' % query
    assert 'api_query' not in obj.__dict__, 'Already has a query %s' % obj
    setattr(obj, 'api_query', query)

def serviceFor(obj, service=None):
    '''
    If the service is provided it will be associate with the obj, if the service is not provided than this function
    will try to provide if it exists the service associated with the obj.
    
    @param obj: object|class
        The class to associate or extract the query.
    @param service: Service
        The Service to associate with the obj.
    @return: Service|None
        If the service has been associate then the return will be none, if the service is being extracted it can
        return either the Service or None if is not found.
    '''
    if service is None:
        return getattr(obj, 'api_service', None)
    assert isinstance(service, Service), 'Invalid service %s' % service
    assert 'api_service' not in obj.__dict__, 'Already has a service %s' % obj
    setattr(obj, 'api_service', service)
