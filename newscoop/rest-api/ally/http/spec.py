'''
Created on Jul 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides specifications for APIs used by the HTTP server.
'''

import abc
from ally.core.internationalization import MessageException
from ally.core.spec.server import Request
from ally.core.spec.codes import Code

# --------------------------------------------------------------------

class RequestHTTP(Request):
    '''
    Provides the request extension with additional HTTP data.
    '''

    def __init__(self):
        '''
        @ivar path: string
            The requested path.
        @ivar headers: dictionary
            The headers of the request
        @ivar input: object
            The object with the 'read(nbytes)' method to provide the content bytes.
        '''
        self.headers = None
        self.input = None
        self.path = None
        super().__init__()

# --------------------------------------------------------------------

class EncoderHeader(metaclass=abc.ABCMeta):
    '''
    Provides the API for encoding the headers from response.
    '''
    
    @abc.abstractmethod
    def encode(self, headers, response):
        '''
        Encode data from the response that is relevant for this encoder in the provided header dictionary.
        
        @param headers: dictionary
            The dictionary containing the headers, as a key the header name.
        @param response: Response
            The response to extract data for the headers from.
        '''

class DecoderHeader(metaclass=abc.ABCMeta):
    '''
    Provides the API for decoding the headers to values.
    '''
    
    @abc.abstractmethod
    def decode(self, request):
        '''
        Decode from the headers the values represented by this decoder.
        
        @param request: RequestHTTP 
            The request to populate the values to.
        '''
        
class ParserHeader(metaclass=abc.ABCMeta):
    '''
    Provides the API for parsing the headers for specific values.
    '''
    
    @abc.abstractmethod
    def parse(self, headers):
        '''
        Parse from the headers the value represented by this parser.
        
        @param headers: dictionary
            The dictionary containing the headers to parse values from.
        @return: object
            The object represented by the parses implementation.
        @raise HeaderException: In case of none or invalid header data. 
        '''

# --------------------------------------------------------------------

class HeaderException(MessageException):
    '''
    Wraps exceptions that are related to header decoding exceptions.
    '''
    
    def __init__(self, message):
        super().__init__(message)

# --------------------------------------------------------------------
# Response HTTP codes.
UNKNOWN_CONTENT_LENGHT = Code(411, False) # HTTP code 411 length required 
UNKNOWN_CONTENT_TYPE = Code(406, False) # HTTP code 406 Not acceptable
UNKNOWN_CHARSET = Code(406, False) # HTTP code 406 Not acceptable
