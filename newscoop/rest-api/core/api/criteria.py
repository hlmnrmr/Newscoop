'''
Created on Jun 10, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides general used criteria for APIs.
'''

from newscoop.core.api.configure import APICriteria as criteria
from newscoop.core.api import configure

# --------------------------------------------------------------------

@criteria()
class AsPaged:
    '''
    Provides paging for queries.
    '''
    offset = int
    limit = int
    
    def toPage(self, page, size):
        '''
        Moves the query to provided page.
        
        @param page: integer
            The page number starting from 1.
        @param size: integer
            The number of elements on a page.
        '''
        self.offset = page * size
        self.limit = size
        
@criteria()
class AsOrdered:
    '''
    Provides query for properties that can be ordered.
    '''
    orderAscending = bool
    
    def orderAsc(self):
        self.orderAscending = True
        
    def orderDesc(self):
        self.orderAscending = False

# register as a default condition for descriptors the like
configure.DEFAULT_CONDITIONS.append('like')

@criteria()
class AsLike(AsOrdered):
    '''
    Provides query for properties that can be managed by a like function.
    '''
    like = str
