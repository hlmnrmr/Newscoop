'''
Created on Jun 5, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the translators that can be used for converting from API models to a serialized format.
'''

import logging
from json.encoder import JSONEncoder

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Translator:
    '''
    Provides the translation of python API objects into serializable formats and vice versa.
    '''
    
    def encode(self, writer, obj):
        '''
        '''
        assert not writer is None and hasattr(writer, 'write'), 'Provide a valid writer with a write method'

        encod = JSONEncoder()
        writer.write(encod.encode(obj))
