'''
Created on Jun 16, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for resources.
'''

from newscoop.api import Entity, IEntityService, QEntity
from ally.core.api.configure import APIModel as model, APIService as service, \
    APIQuery as query, APICall as call
from ally.core.api.criteria import AsLike
from ally.core.api.model import Content

# --------------------------------------------------------------------

@model()
class Resource(Entity):
    '''
    Provides the resource model. Resources provide content that can be managed and used by other services.
    '''
    path = str

# --------------------------------------------------------------------
    
@query(Resource)
class QResource(QEntity):
    '''
    Provides the resource query model.
    '''
    path = AsLike

# --------------------------------------------------------------------

@service(Resource)
class IResourceService(IEntityService):
    '''
    Provides the resource service.
    '''

    @call(Content, Resource.Id)
    def content(self, id):
        '''
        Provides the content stream for the resource.
        
        @param q: The query to search by.
        '''
