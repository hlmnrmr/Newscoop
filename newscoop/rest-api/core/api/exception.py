'''
Created on May 31, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the exceptions that are used in communicating issues in the API.
The internal errors (the ones that are made by the implementation and not data) are AssertionError.
'''

from newscoop.core.internationalization import Message
from newscoop.core.util import guard

# --------------------------------------------------------------------

@guard
class APIException(Exception):
    '''
    Provides the exception that are targeted to reach the API communication.
    So basically this type of exception will be propagated to the client.
    '''

    def __init__(self, message):
        '''
        Initializes the exception based on the message which will be used as a key.
        
        @param msg: string
            The message (that is in English) to be used as a key, this message
            has to contain as many place holders (ex: $1, $2 ...) as there are 
            arguments.
        @param *args: list 
            The arguments to be used instead of the place holders in the message.
        '''
        assert isinstance(message, Message), 'Invalid message %s' % message
        self.message = message
        super().__init__(message.default)

# --------------------------------------------------------------------

class InputException(APIException):
    '''
    Wraps exceptions that are related to input data.
    '''
    
    def __init__(self, message):
        super().__init__(message)
        
class OutputException(APIException):
    '''
    Wraps exceptions that are related to output data.
    '''
    
    def __init__(self, message):
        super().__init__(message)
