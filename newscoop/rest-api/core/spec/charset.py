'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the known character sets.
'''

from newscoop.core.util import Protected, guard

# --------------------------------------------------------------------

@guard
class CharSet(Protected):
    '''
    Contains the character set.
    '''
    
    def __init__(self, format):
        '''
        Constructs the character set.
        
        @param format: string
            The format code string, something like 'UTF-8'.
        '''
        assert isinstance(format, str), 'Invalid format %s' % format
        self.format = format

# --------------------------------------------------------------------
# Character sets.
UTF_8 = CharSet('UTF-8')
