'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for section API.
'''

from newscoop.api.section import ISectionService, Section
from newscoop.impl_alchemy import EntityServiceAlchemy
from ally.core.api.configure import propertiesFor
from ally.core.support.sql_alchemy import mapperModel
from newscoop.impl_alchemy.meta import section as sm

# --------------------------------------------------------------------

mapperModel(Section, sm.table)

# --------------------------------------------------------------------

class SectionServiceAlchemy(EntityServiceAlchemy, ISectionService):
    '''
    Test implementation for @see: ISectionService
    '''
    
    def __init__(self):
        super().__init__(propertiesFor(Section))
        
    def forPublication(self, publicationId, offset=None, limit=None, q=None):
        '''
        @see: ISectionService.forPublication
        '''
        aq = self.session().query(sm.Id).filter(sm.publication == publicationId)
        if q is not None:
            aq = self.buildQuery(aq, q)
        if offset is not None: aq = aq.offset(offset)
        if limit is not None: aq = aq.limit(limit)
        # SQL alchemy returns the id in a tuple
        ids = (tup[0] for tup in aq.all())
        return ids
