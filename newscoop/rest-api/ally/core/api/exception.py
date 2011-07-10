'''
Created on May 31, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the exceptions that are used in communicating issues in the API.
The internal errors (the ones that are made by the implementation and not data) are AssertionError.
'''

from ally.core.internationalization import MessageException

# --------------------------------------------------------------------

class InputException(MessageException):
    '''
    Wraps exceptions that are related to input data.
    '''
    
    def __init__(self, message):
        super().__init__(message)
        
class OutputException(MessageException):
    '''
    Wraps exceptions that are related to output data.
    '''
    
    def __init__(self, message):
        super().__init__(message)
