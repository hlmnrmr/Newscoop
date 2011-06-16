'''
Created on Jun 8, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

API specifications for publication.
'''
from newscoop.core.api.decorator import APIProperty, APICall
from newscoop.api.entity import Entity

class Publication(Entity):
    '''
    Provides the publication model.
    '''
        
    # ----------------------------------------------------------------
    
    @APIProperty(str)
    def name(self):
        '''
        
        '''
    
# --------------------------------------------------------------------

class IPublicationService:
    '''
    Provides services for publication.
    '''
    
    # ----------------------------------------------------------------
    
    def getQuery(self, orderBy=None, offset=0, limit= -1, name=None):
        '''
        use composition with a base implementation
        '''
        print(orderBy)