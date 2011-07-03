'''
Created on Jun 10, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides general used criteria for APIs.
'''

from ally.core.api.configure import APICriteria as criteria
from ally.core.api import configure

# --------------------------------------------------------------------

@criteria()
class AsOrdered:
    '''
    Provides query for properties that can be ordered.
    '''
    orderAscending = bool
    
    def __init__(self):
        self._index = None
        def updateIndex():
            if self._index is None:
                self._index = getattr(self.query, 'asOrderIndex', 1)
                setattr(self.query, 'asOrderIndex', self._index + 1)
        def deleteIndex():
            self._index = None
        self.__dict__['orderAscendingOnSet'] = updateIndex
        self.__dict__['orderAscendingOnDel'] = deleteIndex
    
    def orderAsc(self):
        self.orderAscending = True
        
    def orderDesc(self):
        self.orderAscending = False
        
    def index(self):
        '''
        The index is the position of the ordered in the orders. Basically if you require to know in which order
        the ordering have been provided the index provides that.
        
        @return: integer|None
            The position in the query instance at which this order is considered, the indexes are not required to be
            consecutive in a query. None if there is no ordering ser for this criteria.
        '''
        return self._index

# register as a default condition for descriptors the like
configure.DEFAULT_CONDITIONS.append('like')

@criteria()
class AsLike(AsOrdered):
    '''
    Provides query for properties that can be managed by a like function.
    '''
    like = str
