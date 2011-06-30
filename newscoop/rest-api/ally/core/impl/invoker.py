'''
Created on Jun 25, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invokers implementations.
'''

from _abcoll import Callable
from ally.core.api.operator import Service, Call
from ally.core.spec.resources import Invoker

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
        super().__init__(call.outputType, call.name, call.inputTypes, call.mandatoryCount)

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
    
    def __init__(self, outputType, function, inputTypes, mandatoryCount):
        '''
        @see: Invoker.__init__
        
        @param function: Callable
            The Callable to invoke.
        '''
        assert isinstance(function, Callable), 'Invalid input callable provided %s' % function
        super().__init__(outputType, function.__name__, inputTypes, mandatoryCount)
        self.function = function

    def invoke(self, *args):
        '''
        @see: InvokerCall.invoke
        '''
        return self.function(*args)
