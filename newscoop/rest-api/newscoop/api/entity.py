'''
Created on May 26, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

General specifications for the entities API.
'''

from ally.core.api.configure import APIModel as model, APIService as service, APIQuery as query, \
    APICall as call
from ally.core.api.type import List, Id
from ally.core.api.criteria import AsPaged

# --------------------------------------------------------------------

@model()
class Entity:
    '''
    Provides the basic container for an entity that has a primary key.
    '''
    id = Id

# --------------------------------------------------------------------

@query(Entity)
class QEntity:
    '''
    Provides the basic query for an entity.
    '''
    index = AsPaged
    
# --------------------------------------------------------------------

# The Entity model will be replaced by the specific model when the API will be inherited.
@service(Entity)
class IEntityFindService:
    '''
    Provides the basic entity service. This means locate by id.
    '''
    
    @call(Entity, Entity.id)
    def byId(self, id):
        '''
        Provides the theme based on the theme id.
        '''

# The Entity model will be replaced by the specific model when the API will be inherited.
@service(Entity)
class IEntityCRUDService:
    '''
    Provides the entity the CRUD services.
    '''
    
    @call(bool, Entity)
    def insert(self, entity):
        '''
        Insert the entity.
        
        @return: True if the update is successful, false otherwise.
        '''
        
    @call(bool, Entity)
    def update(self, entity):
        '''
        Update the entity.
        
        @return: True if the update is successful, false otherwise.
        '''
        
    @call(bool, Entity.id)
    def delete(self, id):
        '''
        Delete the entity for the provided id.
        
        @return: True if the delete is successful, false otherwise.
        '''

# The Entity model will be replaced by the specific model when the API will be inherited.
@service(Entity)
class IEntityQueryService(IEntityFindService):
        
    @call(List(Entity.id), QEntity)
    def all(self, q = None):
        '''
        Provides the entities searched by the provided query.
        
        @param q: The query to search by.
        '''
        
# The Entity model will be replaced by the specific model when the API will be inherited.
@service(Entity)
class IEntityService(IEntityQueryService, IEntityCRUDService):
    '''
    Provides the find, CRUD and query entity services.
    '''
