'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing specifications for the server processing.
'''

from ally.core.internationalization import Message
from ally.core.spec.codes import Code
from ally.core.util import guard, injected, Singletone
from collections import deque
import abc

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
        
        @param request: Request
            The request to be processed.
        @param response: Response
            The response to be processed.
        @param chain: ProcessorsChain
            The chain to call the next processors.
        '''

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
        assert isinstance(self.processors, list), 'Invalid processors list %s' % self.processors
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

@guard
class Content(metaclass=abc.ABCMeta):
    '''
    Provides the content of a request.
    '''
    
    def __init__(self, isAvaliable, contentType=None, charSet=None):
        '''
        Constructs the content instance.
        
        @param isAvaliable: boolean
            Flag indicating that there is content available.
        @param contentType: string|None
            The content type for the content if known.
        @param charSet: string|None
            The character set of the content if known.
        '''
        assert isinstance(isAvaliable, bool), 'Invalid available flag %s' % isAvaliable
        assert contentType is None or isinstance(contentType, str), 'Invalid content type %s' % contentType
        assert charSet is None or isinstance(charSet, str), 'Invalid character set %s' % charSet
        self.isAvaliable = isAvaliable
        self.contentType = contentType
        self.charSet = charSet
    
    @abc.abstractmethod
    def read(self, nbytes=None):
        '''
        Reads nbytes from the content, attention the content can be read only once.
        
        @param nbytes: integer|None
            The number of bytes to read, or None to read all remaining available bytes from the content.
        '''
        
class ContentNone(Singletone, Content):
    '''
    Singletone class that provides a not available content type implementation.
    '''
    
    def __init__(self):
        Content.__init__(self, False)
        
    def read(self, nbytes=None):
        '''
        @see: Content.read
        '''
        raise AssertionError('No content available')
    
class ContentOnFile(Content):
    '''
    Implementation for content that provides data from a file. A file means any object that has the 'read(nbytes)'
    method.
    '''
    
    def __init__(self, file, length=None, contentType=None, charSet=None):
        '''
        @see: Content.__init__
        
        @param file: object
            The object with the 'read(nbytes)' method to provide the content bytes.
        @param length: integer|None
            The number of available bytes in the content, if None it means that is not known.
        '''
        assert file is not None and getattr(file, 'read') is not None, 'Invalid file object %s' % file
        assert length is None or isinstance(length, int), 'Invalid length %s, can be None' % length
        super().__init__(True, contentType, charSet)
        self.file = file
        self.length = length
        self._offset = 0
        
    def read(self, nbytes=None):
        '''
        @see: Content.read
        '''
        count = nbytes
        if self.length is not None:
            if self._offset >= self.length:
                return ''
            delta = self.length - self._offset
            if count is None:
                count = delta
            elif count > delta:
                count = delta
        bytes = self.file.read(count)
        self._offset += len(bytes)
        return bytes

# --------------------------------------------------------------------
# The available request methods.
GET = 1
INSERT = 2
UPDATE = 4
DELETE = 8

class Request:
    '''
    Maps a request object based on a request path and action.
    '''
    
    def __init__(self):
        '''
        @ivar method: integer
            The method of the request, can be one of GET, INSERT, UPDATE or DELETE constants in this module.
        @ivar accContentTypes: list
            The content types accepted for response
        @ivar accCharSets: list
            The character sets accepted for response
        @ivar content: Content
            The content provider for the request.
        @ivar resourcePath: Path
            The path to the resource node.
        @ivar params: list
            A list of tuples containing on the first position the parameter string name and on the second the string
            parameter value as provided in the request path. The parameters need to be transformed into arguments
            and also removed from this list while doing that.
            I did not use a dictionary on this since the parameter names might repeat and also the order might be
            important.
        @ivar arguments: dictionary
            A dictionary containing as a key the argument name, this dictionary needs to be populated by the 
            processors as seen fit, also the parameters need to be transformed to arguments.
        @ivar obj: object
            The object to be rendered.
        @ivar objType: Type
            The type of the object to be rendered.
        '''
        self.method = None
        self.accContentTypes = None
        self.accCharSets = None
        self.content = None
        self.resourcePath = None
        self.params = None
        self.arguments = None
        self.obj = None
        self.objType = None

# --------------------------------------------------------------------

class Response(metaclass=abc.ABCMeta):
    '''
    Provides the response support.
    '''
    
    def __init__(self):
        '''
        @ivar code: Code
            The code of the response, do not update this directly use a one of the methods.
        @ivar message: Message
            A message for the code, do not update this directly use a one of the methods.
        @ivar charSet: string
            The character set for the response, do not update this directly use a one of the methods.
        @ivar contentType: string
            The content type for the response, do not update this directly use a one of the methods.
        @ivar allows: integer
            Contains the allow flags for the methods.
        @ivar encoderPath: EncoderPath
            The path encoder used for encoding paths that will be rendered in the response.
        @ivar encoder: Encoder
            The encoder used for encoding the content of the response.
        '''
        self.code = None
        self.message = None
        self.charSet = None
        self.contentType = None
        self.allows = 0
        self.encoderPath = None
        self.encoder = None
    
    def addAllows(self, method):
        '''
        Set the status of allowing get method. 
        
        @param method: integer
            The method of the request, can be one of GET, INSERT, UPDATE or DELETE constants in this module.
        '''
        assert isinstance(method, int), \
        'Invalid method %s, needs to be one of the integer defined request methods' % method
        self.allows |= method

    def setCode(self, code, message):
        '''
        Sets the provided code.
        
        @param code: Code
            The code to set.
        @param message: string
            The message to send in relation to the code.
        '''
        assert isinstance(code, Code), 'Invalid code %s' % code
        assert isinstance(message, Message), 'Invalid message %s' % message
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
