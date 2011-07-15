'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for issue API.
'''

from newscoop.impl_alchemy import EntityServiceAlchemy
from ally.core.api.configure import propertiesFor
from ally.core.support.sql_alchemy import mapperModel
from newscoop.impl_alchemy.meta import issue as im
from newscoop.api.issue import Issue, IIssueService

# --------------------------------------------------------------------

mapperModel(Issue, im.table)

# --------------------------------------------------------------------

class IssueServiceAlchemy(EntityServiceAlchemy, IIssueService):
    '''
    Test implementation for @see: IIssueService
    '''
    
    def __init__(self):
        super().__init__(propertiesFor(Issue))
        
    def forPublication(self, publicationId, offset=None, limit=None, q=None):
        '''
        @see: ISectionService.forPublication
        '''
        aq = self.session().query(im.Id).filter(im.publication == publicationId)
        if q is not None:
            aq = self.buildQuery(aq, q)
        if offset is not None: aq = aq.offset(offset)
        if limit is not None: aq = aq.limit(limit)
        # SQL alchemy returns the id in a tuple
        ids = (tup[0] for tup in aq.all())
        return ids
