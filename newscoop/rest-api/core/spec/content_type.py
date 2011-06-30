'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the known content types.
'''

from newscoop.core.util import Protected, guard

# --------------------------------------------------------------------

@guard
class ContentType(Protected):
    '''
    Contains the content type.
    '''
    
    def __init__(self, format, content):
        '''
        Constructs the content type.
        
        @param format: string
            The format of the content, this has to be lower case.
        @param content: string
            The type of the content.
        '''
        assert isinstance(format, str), 'Invalid format %s' % format
        assert isinstance(content, str), 'Invalid content type %s' % content
        self.format = format.lower()
        self.content = content

# --------------------------------------------------------------------
# Character sets.
XML = ContentType('xml', 'text/xml')
