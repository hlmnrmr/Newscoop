'''
Created on Jun 25, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invokers implementations.
'''

from _abcoll import Callable
from ally.core.api.operator import Service, Call, Property
from ally.core.spec.resources import Invoker
from ally.core.api.type import TypeProperty, Input

# --------------------------------------------------------------------

class InvokerCall(Invoker):
    '''
    Provides invoking for API calls.
    '''
    
    def __init__(self, service, implementation, call):
        '''
        @see: Invoker.__init__
        
        @param service: Service
            The service for the call of the access.
        @param implementation: object
            The implementation for the call of the access.
        @param call: Call
            The call of the access.
        '''
        assert isinstance(service, Service), 'Invalid service %s' % service
        assert isinstance(call, Call), 'Invalid call %s' % call
        self.service = service
        self.implementation = implementation
        self.call = call
        super().__init__(call.outputType, call.name, call.inputs, call.mandatoryCount)

    def invoke(self, *args):
        '''
        @see: InvokerCall.invoke
        '''
        return self.call.call(self.implementation, args)

# --------------------------------------------------------------------

class InvokerFunction(Invoker):
    '''
    Provides invoking for API calls.
    '''
    
    def __init__(self, outputType, function, inputs, mandatoryCount):
        '''
        @see: Invoker.__init__
        
        @param function: Callable
            The Callable to invoke.
        '''
        assert isinstance(function, Callable), 'Invalid input callable provided %s' % function
        super().__init__(outputType, function.__name__, inputs, mandatoryCount)
        self.function = function

    def invoke(self, *args):
        '''
        @see: InvokerCall.invoke
        '''
        return self.function(*args)

# --------------------------------------------------------------------

class InvokerUpdateModel(Invoker):
    '''
    Wraps an update invoker that has the signature like bool%(Entity) to look like bool%(Entity.Id, Entity) which
    is the form that is called by the delete action.
    '''
    
    def __init__(self, invoker, typeProperty):
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(typeProperty, TypeProperty), 'Invalid type property %s' % typeProperty
        modelInput = invoker.inputs[0]
        inputs = [Input(modelInput.name + 'Id', typeProperty), modelInput]
        super().__init__(invoker.outputType, invoker.name, inputs, len(inputs))
        self.invoker = invoker
        self.property = typeProperty.property
        
    def invoke(self, *args):
        '''
        First argument is the id and the second the entity.
        @see: Invoker.invoke
        '''
        prop = self.property
        assert isinstance(prop, Property)
        prop.set(args[1], args[0])
        return self.invoker.invoke(args[1])
