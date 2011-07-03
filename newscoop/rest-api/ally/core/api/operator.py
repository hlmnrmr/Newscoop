'''
Created on May 29, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the containers that describe the APIs.
'''

from inspect import ismodule, getargspec, isclass
from ally.core.api.exception import InputException, OutputException
from ally.core.api.type import Type, TypeClass, Input
from ally.core.internationalization import msg as _
from ally.core.util import simpleName, guard
import logging
from _abcoll import Iterable

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@guard
class Properties:
    '''
    Used for mapping the API properties.
    '''

    def __init__(self, properties):
        '''
        Constructs a properties group.
        
        @param properties: dictionary
            A dictionary containing as a key the property name and as a value the property.
        '''
        assert isinstance(properties, dict), 'The properties %s need to be a dictionary' % properties
        if __debug__:
            for prop in properties.values():
                assert isinstance(prop, Property), 'Not a Property type for %s' % prop
        self.properties = properties
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.properties == other.properties
        return False
    
    def __str__(self):
        return '<%s %s>' % (simpleName(self), [str(prop) for prop in self.properties.values()])

@guard
class Property:
    '''
    Provides the container for the API property types. It contains the operation that need to be
    applied on a model instance that relate to this property.
    The property operator also provides a listener mechanism whenever the represented property this to be notified
    for changes to the contained model. So if we have property 'name' automatically whenever the value is set if
    the model contains the 'nameOnSet' method it will be called, and on deletion the 'nameOnDel' is called.
    '''

    def __init__(self, name, type):
        '''
        Constructs a property operations container.
        
        @param name: string
            The name of the property as it should be called by.
        @param type: Type
            The Type of the property.
        @ivar _var: string
            Contains the name of the attribute that will be used for keeping the property value.
        '''
        assert isinstance(name, str) and str != '', 'Provide a valid name'
        assert isinstance(type, Type), 'Invalid type %s' % type
        self.type = type
        self.name = name
        # The name of the attributes that are placed in the model automatically.
        self._var = 'prop_' + name
    
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
        if not value is None and not self.type.isValid(value):
            raise InputException(_('The property $1 takes a parameter of type $2, illegal value $3',
                                 self.name, self.type, value))
        setattr(model, self._var, value)
        listener = getattr(model, self.name + 'OnSet', None)
        if listener is not None:
            listener()
        log.debug('Success on setting value (%s) for %s', value, self)
    
    def remove(self, model):
        '''
        Remove the value represented by this property from the provided model instance.
        
        @param model: object
            The model instance to remove the value from.
        @return: boolean
            True if there has been something to remove, false otherwise.
        '''
        assert not model is None, 'Invalid model object (None)'
        if hasattr(model, self._var):
            delattr(model, self._var)
            listener = getattr(model, self.name + 'OnDel', None)
            if listener is not None:
                listener()
            log.debug('Success on removing value for %s', self)
            return True
        return False
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.type == other.type
        return False

    def __str__(self):
        return '<%s[%s = %s]>' % (simpleName(self), self.name, self.type)

# --------------------------------------------------------------------

@guard(ifNoneSet='query')
class Model(Properties):
    '''
    Used for mapping the API models.
    @attention: The model will allow only for primitive types.
    @see: Properties
    '''

    def __init__(self, modelClass, properties):
        '''
        Constructs a properties model.
        @see: Properties.__init__
        
        @param modelClass: class
            The represented model class.
        @ivar query: Query
            The query of the model, needs to be assigned by the declared query for the model.
        @ivar name: string
            The name of the model.
        '''
        assert isclass(modelClass), 'Invalid model class %s' % modelClass
        self.modelClass = modelClass
        self.name = simpleName(modelClass)
        self.query = None
        super().__init__(properties)
        if __debug__:
            for prop in properties.values():
                assert prop.type.isPrimitive, 'Not a primitive type for %s' % prop

    def __eq__(self, other):
        if super().__eq__(other):
            return self.modelClass == other.modelClass and self.name == other.name
        return False

    def __str__(self):
        return '<%s (%s) %s>' % (simpleName(self), self.name, \
                                 [str(prop) for prop in self.properties.values()])
       
# --------------------------------------------------------------------

@guard
class Query:
    '''
    Used for mapping the API query.
    '''

    def __init__(self, queryClass, criteriaEntries):
        '''
        Initialize the criteria's of this query.
        
        @param queryClass: class
            The represented query class.
        @param criteriaEntries: dictionary
            The criteria's dictionary that belong to this query, as a key is the criteria name (how is been 
            declared in the query) and as a value the criteria entry.
        '''
        assert isclass(queryClass), 'Invalid query class %s' % queryClass
        assert isinstance(criteriaEntries, dict), \
        'The criteria entries %s needs to be a dictionary' % criteriaEntries
        if __debug__:
            for crt in criteriaEntries.values():
                assert isinstance(crt, CriteriaEntry), 'Not a CriteriaEntry %s' % crt
        self.queryClass = queryClass
        self.criteriaEntries = criteriaEntries

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.queryClass == other.queryClass and self.criteriaEntries == other.criteriaEntries
        return False

    def __str__(self):
        return '<%s %s>' % (simpleName(self.queryClass), [str(entry) for entry in self.criteriaEntries.values()])
 
class CriteriaEntry(Property):
    '''
    Contains a criteria entry in a query. 
    @see: Property
    '''
    
    def __init__(self, criteria, name):
        '''
        Constructs a criteria entry.
        @see: Property.__init__
        
        @param criteria: Criteria
            The criteria that is being used by this entry.
        '''
        assert isinstance(criteria, Criteria), 'Invalid criteria %s' % criteria
        self.criteria = criteria
        super().__init__(name, TypeClass(criteria.criteriaClass))

class Criteria(Properties):
    '''
    Used for mapping the API criteria.
    @attention: The criteria will allow only for primitive types.
    @see: Properties
    '''

    def __init__(self, criteriaClass, properties):
        '''
        Initialize the criteria instance by providing the name under which the criteria has been declared.
        @see: Properties.__init__
        
        @param criteriaClass: class
            The represented criteria class.
        '''
        assert isclass(criteriaClass), 'Invalid criteria class %s' % criteriaClass
        self.criteriaClass = criteriaClass
        super().__init__(properties)
        if __debug__:
            for prop in properties.values():
                assert prop.type.isPrimitive, 'Not a primitive type for %s' % prop

    def __eq__(self, other):
        if super().__eq__(other):
            return self.criteriaClass == other.criteriaClass
        return False
    
# --------------------------------------------------------------------

@guard
class Call:
    '''
    Provides the container for a service call. This class will basically contain all the
    Property types that are involved in input and output from the call.
    '''
    
    def __init__(self, name, outputType, inputs, mandatoryCount):
        '''
        Constructs an API call that will have the provided input and output types.
        
        @param name: string
            The name of the function that will be called on the service implementation.
        @param outputType: Type
            The output type for the service call.
        @param inputs: list
            A list containing all the Input's of the call.
        @param mandatoryCount: integer
            Provides the count of the mandatory input types, if the mandatory count is two and we have three input
            types it means that just the first two parameters need to be provided.
        '''
        assert isinstance(name, str) and str != '', 'Provide a valid name'
        assert isinstance(outputType, Type), 'Invalid output Type %s' % outputType
        assert isinstance(inputs, list), 'Invalid inputs %s, needs to be a list' % inputs
        assert isinstance(mandatoryCount, int), 'Invalid mandatory count <%s>, needs to be integer' % mandatoryCount
        assert mandatoryCount >= 0 and mandatoryCount <= len(inputs), \
        'Invalid mandatory count <%s>, needs to be greater than 0 and less than ' % (mandatoryCount, len(inputs))
        if __debug__:
            for input in inputs:
                assert isinstance(input, Input), 'Not an input %s' % input
        self.name = name
        self.outputType = outputType
        self.inputs = inputs
        self.mandatoryCount = mandatoryCount

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
        @param args: list
            The arguments to be used in invoking the service 
        '''
        assert not impl is None, 'Provide the service implementation to be used foe calling the represented function'
        assert isinstance(args, Iterable), 'The arguments %s need to be iterable' % str(args)
        valid = False
        if len(args) >= self.mandatoryCount and len(self.inputs) >= len(args):
            valid = True
            for inp, value in zip(self.inputs, args):
                assert isinstance(inp, Input)
                if not inp.type.isValid(value):
                    valid = False
                    break
        if not valid:
            raise InputException(_('The arguments $1 provided are not compatible with the expected inputs $2',
                                 args, self.inputs))
        if ismodule(impl):
            func = getattr(impl, self.name)
            ret = func.__call__(*args)
        else:
            func = getattr(impl.__class__, self.name)
            ret = func.__call__(impl, *args)
            
        if not self.outputType.isValid(ret):
            raise OutputException(_('The return $1 provided is not compatible with the expected output type $2',
                                 ret, self.outputType))
        
        log.debug('Success calling <%s> with arguments %s and return class %s', \
                  func.__name__, args, simpleName(ret))
        return ret
    
    def _findClassFunction(self, implClass):
        '''
        Finds the class function that is represented by this call.
        
        @return: function|None
            Returns the function if found for the provided class or None
            if no such function could be located.
        '''
        func = getattr(implClass, self.name, None)
        if not func is None:
            fnArgs = getargspec(func)
            if len(fnArgs.args) == 1 + len(self.inputs):
                if fnArgs.defaults is None:
                    if len(self.inputs) - self.mandatoryCount == 0:
                        return func
                elif len(self.inputs) - self.mandatoryCount == len(fnArgs.defaults):
                    return func
                        
    def _findModuleFunction(self, implModule):
        '''
        Finds the module function that is represented by this call.
        
        @return: function|None
            Returns the function if found for the provided module or None
            if no such function could be located.
        '''
        func = getattr(implModule, self.name, None)
        if not func is None:
            fnArgs = getargspec(func)
            if len(fnArgs.args) == len(self.inputs):
                if fnArgs.defaults is None:
                    if len(self.inputs) - self.mandatoryCount == 0:
                        return func
                elif len(self.inputs) - self.mandatoryCount == len(fnArgs.defaults):
                    return func

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.outputType == other.outputType \
                and self.inputs == other.inputs and self.mandatoryCount == other.mandatoryCount
        return False
    
    def __str__(self):
        inputStr = []
        for i, inp in enumerate(self.inputs):
            assert isinstance(inp, Input)
            inputStr.append(('defaulted:' if i >= self.mandatoryCount else '') + inp.name + '=' + str(inp.type))
        return '<Call[%s %s(%s)]>' % (self.outputType, self.name, ', '.join(inputStr))

@guard
class Service:
    '''
    Used for mapping the API calls.
    '''

    def __init__(self, model, serviceClass, calls):
        '''
        Constructs the API service class based on the provided implementation.
        
        @param model: class
            The model that represents the service.
        @param calls: dictionary
            The calls dictionary that belong to this service class, the key is the call name.
        '''
        assert isclass(serviceClass), 'Invalid service class %s' % serviceClass
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(calls, dict), 'The calls %s need to be a dictionary' % calls
        if __debug__:
            for call in calls.values():
                assert isinstance(call, Call), 'Not a Call type for %s' % call
        self.model = model
        self.serviceClass = serviceClass
        self.calls = calls

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.serviceClass == other.serviceClass and self.model == other.model \
                and self.calls == other.calls
        return False
    
    def __str__(self):
        return '<Service[%s(%s) %s calls]>' % \
            (simpleName(self.serviceClass), self.model.name, len(self.calls))
