'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Module containing specifications for the server processing.
'''
from collections import deque
from newscoop.core.api.type import Type
from newscoop.core.spec.resources import Path
from newscoop.core.util import guard
import abc
from newscoop.core.internationalization import Message
from newscoop.core.spec.charset import CharSet
from newscoop.core.spec.content_type import ContentType
from newscoop.core.spec.codes import Code

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

# --------------------------------------------------------------------

@guard
class Request:
    '''
    Maps a request object based on a request path and action.
    '''
    
    def __init__(self, requestPath):
        '''
        Constructs the request.
        
        @param requestPath: string
            The requested path.
        '''
        assert isinstance(requestPath, str), 'Invalid request path %s' % requestPath
        self.requestPath = requestPath

class RequestGet(Request):
    '''
    Maps the get requests.
    '''
    
    def __init__(self, requestPath):
        '''
        @see: Request.__init__
        '''
        super().__init__(requestPath)

@guard
class RequestResource:
    '''
    Provides the requested resource data.
    '''
    
    def __init__(self, request, path):
        '''
        Constructs the resource request.
        
        @param request: Request
            The request that this resource request is based on.
        @param path: Path
            The path to the resource node.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(path, Path), 'Invalid resource path %s' % path
        self.request = request
        self.path = path

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
        
        @ivar code: integer
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
    
# --------------------------------------------------------------------

@guard
class EncoderPath(metaclass=abc.ABCMeta):
    '''
    Provides the path encoding.
    '''
    
    @abc.abstractmethod
    def encode(self, path):
        '''
        Encodes the provided path to a full request path.
        
        @param path: Path
            The path to be encoded.
        @return: object
            The full compiled request path, the type depends on the implementation.
        '''

@guard
class Encoder(metaclass=abc.ABCMeta):
    '''
    Provides the base class for the encoders.
    '''
    
    @abc.abstractmethod
    def open(self, name):
        '''
        Opens a new containing block of sub elements.
        Attention each block opened needs to be closed, and all succeeding elements belong to the currently
        open block.
        
        @param name: string
            The name of the block.
        '''
    
    @abc.abstractmethod
    def put(self, name, value, path=None):
        '''
        Encode the name value pair.
        
        @param name: string
            The name of the element.
        @param value: object
            The element value to encode, the type is mostly depended on the encoder implementation.
        @param path: Path
            A path linking the element.
        '''
    
    @abc.abstractmethod
    def close(self):
        '''
        Close the currently opened block.
        
        @return: string
            The name of the closed block.
        '''

@guard
class EncoderFactory(metaclass=abc.ABCMeta):
    '''
    Factory for providing encoders.
    '''
    
    def __init__(self, contentType):
        '''
        Constructs the encoder path.
        
        @param contentType: ContentType
            The content type of the encoder factory.
        '''
        assert isinstance(contentType, ContentType), 'Invalid content type %s' % contentType
        self.contentType = contentType
    
    @abc.abstractmethod
    def isValidFormat(self, format):
        '''
        Checks if the provided format is valid for this encoder factory.
        
        @param format: object
            The format desired.
        '''
    
    @abc.abstractmethod
    def createEncoder(self, encoderPath, out):
        '''
        Creates an encoder specific for this path encoder for the provided output.
        
        @param encoderPath: EncoderPath
            The path encoder that will be used by the encoder to code the paths.
        @param out: Callable
            The output Callable used for writing content.
        @return: Encoder
            The new encoder.
        '''

# --------------------------------------------------------------------

class Render:
    '''
    Class that handles the rendering of model objects to encoders.
    '''
    
    def render(self, obj, objType, encoder):
        '''
        '''
    
    
