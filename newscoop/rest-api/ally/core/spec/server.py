'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing specifications for the server processing.
'''

from collections import deque
from ally.core.api.type import Type
from ally.core.internationalization import Message
from ally.core.spec.charset import CharSet
from ally.core.spec.codes import Code
from ally.core.spec.content_type import ContentType
from ally.core.spec.resources import Path
from ally.core.util import guard, injected
import abc
from ally.core.spec.presenting import EncoderPath

# --------------------------------------------------------------------

@guard
class Processor(metaclass=abc.ABCMeta):
    '''
    Provides the specifications for all processor classes.
    '''
    
    @abc.abstractmethod
    def process(self, request, response, chain):
        '''
        Processes the filtering, the processor has the duty to proceed by calling the chain.
        
        @param request: object
            The request to be processed.
        @param response: object
            The response to be processed.
        @param chain: ProcessorsChain
            The chain to call the next processors.
        '''
        
    def findResponseIn(self, response):
        '''
        Finds the Response instance for the provided response object. This class actually tries the response even
        if the response is encapsulated in within another response type object.
        
        @param response: object
            The response object in which to find the Response.
        @return: Response|None
            The Response instance or None if no response could be located. 
        '''
        if isinstance(response, Response):
            return response
        if isinstance(response, ResponseFormat):
            return response.response
        return None

@guard
class ProcessorsChain:
    '''
    A chain that contains a list of processors that are executed one by one. Each processor will have the duty
    to proceed with the processing if is the case by calling the chain.
    '''
    
    def __init__(self, processors):
        '''
        Initializes the chain with the processors to be executed.
        
        @param processors: list
            The list of processors to be executed. Attention the order in which the processors are provided
            is critical.
        '''
        assert isinstance(processors, list), 'Invalid processors list %s' % processors
        if __debug__:
            for processor in processors:
                assert isinstance(processor, Processor), 'Invalid processor %s' % processor
        self._processors = deque(processors)
    
    def process(self, request, response):
        '''
        Called in order to execute the next processors in the chain. This method will stop processing when all
        the processors have been executed.
        
        @param request: object
            The request to dispatch to the next processors to be executed.
        @param response: object
            The response to dispatch to the next processors to be executed.
        '''
        if len(self._processors) > 0:
            proc = self._processors.popleft()
            assert isinstance(proc, Processor)
            proc.process(request, response, self)

@injected
class Processors:
    '''
    Container for processor's, also provides chains for their execution.
    '''
    
    processors = list
    # The list of processors that compose this container.
    
    def __init__(self):
        if __debug__:
            for processor in self.processors:
                assert isinstance(processor, Processor), 'Invalid processor %s' % processor
         
    def newChain(self):
        '''
        Constructs a new processors chain.
        
        @return: ProcessorsChain
            The chain of processors.
        '''
        return ProcessorsChain(self.processors)
        
# --------------------------------------------------------------------
# The available request methods.
GET = 1
INSERT = 2
UPDATE = 4
DELETE = 8

@guard(allow='method')
class Request:
    '''
    Maps a request object based on a request path and action.
    '''
    
    def __init__(self, method, requestPath):
        '''
        Constructs the request.
        
        @param requestPath: string
            The requested path.
        @param method: integer
            The method of the request, can be one of GET, INSERT, UPDATE or DELETE constants in this module.
        '''
        assert isinstance(method, int), \
        'Invalid method %s, needs to be one of the integer defined request methods' % method
        assert isinstance(requestPath, str), 'Invalid request path %s' % requestPath
        self.method = method
        self.requestPath = requestPath

@guard
class RequestResource:
    '''
    Provides the requested resource data.
    '''
    
    def __init__(self, request, path, parameters):
        '''
        Constructs the resource request.
        
        @param request: Request
            The request that this resource request is based on.
        @param path: Path
            The path to the resource node.
        @param params: list
            A list of tuples containing on the first position the parameter string name and on the second the string
            parameter value as provided in the request path. The parameters need to be transformed into arguments
            and also removed from this list while doing that.
            I did not use a dictionary on this since the parameter names might repeat and also the order might be
            important.
        @ivar arguments: dictionary
            A dictionary containing as a key the argument name, this dictionary needs to be populated by the 
            processors as seen fit, also the parameters need to be transformed to arguments.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(path, Path), 'Invalid resource path %s' % path
        assert isinstance(parameters, list), 'Invalid parameters list %s' % parameters
        if __debug__:
            for param in parameters:
                assert isinstance(param, tuple), 'Invalid parameter %s, needs to be a tuple' % param
                assert len(param) == 2, 'Invalid parameter %s, needs to have two elements' % param
                assert isinstance(param[0], str) and isinstance(param[1], str), \
                'Invalid parameter %s, needs to contain only strings' % param
        self.request = request
        self.path = path
        self.parameters = parameters
        self.arguments = {}

@guard
class RequestRender:
    '''
    Provides the request for rendering the response based on the provided object and object type. 
    '''
    
    def __init__(self, requestResource, obj, objType):
        '''
        Constructs the render request.
        
        @param requestResource: RequestResource
            The request resource that generated the render request.
        @param obj: object
            The object to be rendered.
        @param objType: Type
            The type of the object to be rendered.
        '''
        assert isinstance(requestResource, RequestResource), 'Invalid resource request %s' % requestResource
        assert isinstance(objType, Type), 'Invalid object type %s' % objType
        self.requestResource = requestResource
        self.obj = obj
        self.objType = objType
    
# --------------------------------------------------------------------

@guard
class Response(metaclass=abc.ABCMeta):
    '''
    Provides the response support.
    '''
    
    def __init__(self):
        '''
        Constructs the response. 
        
        @ivar code: Code
            The code of the response, do not update this directly use a one of the methods.
        @ivar message: Message
            A message for the code, do not update this directly use a one of the methods.
        @ivar charSet: string
            The character set for the response, do not update this directly use a one of the methods.
        @ivar contentType: string
            The content type for the response, do not update this directly use a one of the methods.
        '''
        self.code = None
        self.message = None
        self.charSet = None
        self.contentType = None
        self.allows = 0
    
    def setCharSet(self, charSet):
        '''
        Sets to the response header the content character set.
        
        @param charSet: CharSet
            The character set for the response.
        '''
        assert isinstance(charSet, CharSet), 'Invalid character set %s' % charSet
        self.charSet = charSet
    
    def setContentType(self, contentType):
        '''
        Sets to the response header the content type.
        
        @param contentType: ContentType
            The content type format.
        '''
        assert isinstance(contentType, ContentType), 'Invalid content type %s' % contentType
        self.contentType = contentType
    
    def setAllows(self, method):
        '''
        Set the status of allowing get method. 
        
        @param method: integer
            The method of the request, can be one of GET, INSERT, UPDATE or DELETE constants in this module.
        '''
        assert isinstance(method, int), \
        'Invalid method %s, needs to be one of the integer defined request methods' % method
        self.allows |= method

    def setCode(self, code, message=None):
        '''
        Sets the provided code.
        
        @param code: Code
            The code to set.
        @param message: string
            The message to send in relation to the code.
        '''
        assert isinstance(code, Code), 'Invalid code %s' % code
        assert message is None or isinstance(message, Message), 'Invalid message %s' % message
        self.code = code
        self.message = message

    @abc.abstractmethod
    def dispatch(self):
        '''
        Dispatches the response and returns a writer object that has a 'write' method, used for outputting the
        content. Calling this method will also close the response no more actions can be performed.
        
        @return: object 
            A writer object that has a 'write' method, used for outputting the content.
        '''

@guard
class ResponseFormat:
    '''
    Maps the response with an additional encoder path. 
    '''
    
    def __init__(self, response, encoderPath, format):
        '''
        Constructs the response encoder path.
        
        @param response: Response
            The response that this response encoder path is based on.
        @param encoderPath: EncoderPath
            The path encoder used for encoding paths that will be rendered in the response.
        @param format: string|None
            The requested format for the resource.
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(encoderPath, EncoderPath), 'Invalid path encoder %s' % encoderPath
        assert format is None or isinstance(format, str), 'Invalid format name %s' % format
        self.response = response
        self.encoderPath = encoderPath
        self.format = format
