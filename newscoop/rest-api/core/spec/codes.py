'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Contains the codes to be used for the server responses.
'''

from newscoop.core.util import Protected, guard

# --------------------------------------------------------------------

@guard
class Code(Protected):
    '''
    Contains the server code.
    '''
    
    def __init__(self, code, isSuccess):
        '''
        Constructs the code.
        
        @param code: integer
            The integer code corresponding to this code.
        @param isSuccess: boolean
            Flag indicating if the code is a fail or success code.
        '''
        assert isinstance(code, int), 'Invalid code %s' % code
        assert isinstance(isSuccess, bool), 'Invalid success flag %s' % isSuccess
        self.code = code
        self.isSuccess = isSuccess

# --------------------------------------------------------------------
# Response codes.
INTERNAL_ERROR = Code(500, False) # HTTP code 500 Internal Server Error
UNKNOWN_FORMAT = Code(400, False) # HTTP code 400 Bad Request
RESOURCE_NOT_FOUND = Code(404, False) # HTTP code 404 Not Found
NOT_AVAILABLE = Code(405, False) # HTTP code 405 Method Not Allowed

RESOURCE_FOUND = Code(200, True) # HTTP code 200 OK
