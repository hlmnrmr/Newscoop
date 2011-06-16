'''
Created on May 26, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

General specifications for the entities API.
'''
from newscoop.core.api.decorator import APIModel, APIProperty as prop
from newscoop.core.api.type import Integer

@APIModel()
class Entity:
    '''
    Provides the basic container for an entity that has a primary key.
    '''
        
    # ----------------------------------------------------------------
    
    @prop(Integer)
    def id(self):
        '''
        The id of the entity, this will uniquielly identify this output.
        
        @param id: integer 
            The id of the entity, (specify to set).
        @return: integer
            The id of the entity.
        '''
