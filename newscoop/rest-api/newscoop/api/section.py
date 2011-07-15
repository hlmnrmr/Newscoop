'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for section.
'''

from newscoop.api import Entity, IEntityService, QEntity
from ally.core.api.configure import APIModel as model, APIService as service, \
    APIQuery as query, APICall as call
from ally.core.api.criteria import AsLike
from ally.core.api.type import Iter
from newscoop.api.publication import Publication

# --------------------------------------------------------------------

@model()
class Section(Entity):
    '''
    Provides the section model.
    '''
    Name = str
    Description = str

# --------------------------------------------------------------------

@query(Section)
class QSection(QEntity):
    '''
    Provides the section query model.
    '''
    name = AsLike
    description = AsLike

# --------------------------------------------------------------------

@service(Section)
class ISectionService(IEntityService):
    '''
    Provides services for sections.
    '''
    
    @call(Iter(Section.Id), Publication.Id, int, int, QSection)
    def forPublication(self, publicationId, offset=None, limit=None, q=None):
        '''
        Provides all the sections that belong to the publication.
        
        @param publicationId: integer
            The publication if to retrieve the sections from.
        @param offset: integer
            The offset to retrieve the sections from.
        @param limit: integer
            The limit of sections to retrieve.
        @param q: QSection
            The query to search by.
        '''
