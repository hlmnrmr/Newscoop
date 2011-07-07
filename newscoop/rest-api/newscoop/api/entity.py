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
from ally.core.api.type import Id, Iter

# --------------------------------------------------------------------

@model()
class Entity:
    '''
    Provides the basic container for an entity that has a primary key.
    '''
    Id = Id

# --------------------------------------------------------------------

@query(Entity)
class QEntity:
    '''
    Provides the basic query for an entity.
    '''
    
# --------------------------------------------------------------------

# The Entity model will be replaced by the specific model when the API will be inherited.
@service(Entity)
class IEntityFindService:
    '''
    Provides the basic entity service. This means locate by id.
    '''
    
    @call(Entity, Entity.Id)
    def byId(self, id):
        '''
        Provides the entity based on the id.
        
        @raise InputException: If the id is not valid. 
        '''

# The Entity model will be replaced by the specific model when the API will be inherited.
@service(Entity)
class IEntityCRUDService:
    '''
    Provides the entity the CRUD services.
    '''
    
    @call(Entity.Id, Entity)
    def insert(self, entity):
        '''
        Insert the entity.
        
        @return: The id of the entity
        @raise InputException: If the entity is not valid. 
        '''
        
    @call(bool, Entity)
    def update(self, entity):
        '''
        Update the entity.
        
        @return: True if the update is successful, false otherwise.
        '''
        
    @call(bool, Entity.Id)
    def delete(self, id):
        '''
        Delete the entity for the provided id.
        
        @return: True if the delete is successful, false otherwise.
        '''

# The Entity model will be replaced by the specific model when the API will be inherited.
@service(Entity)
class IEntityQueryService(IEntityFindService):
        
    @call(Iter(Entity.Id), int, int, QEntity)
    def all(self, offset=None, limit=None, q=None):
        '''
        Provides the entities searched by the provided query.
        
        @param offset: integer
            The offset to retrieve the entities from.
        @param limit: integer
            The limit of entities to retrieve.
        @param q: QEntity
            The query to search by.
        '''
        
# The Entity model will be replaced by the specific model when the API will be inherited.
@service(Entity)
class IEntityService(IEntityQueryService, IEntityCRUDService):
    '''
    Provides the find, CRUD and query entity services.
    '''
