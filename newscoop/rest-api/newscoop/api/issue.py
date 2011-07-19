'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for issues.
'''

from newscoop.api import Entity, IEntityService, QEntity
from ally.core.api.configure import APIModel as model, APIService as service, \
    APIQuery as query, APICall as call
from ally.core.api.criteria import AsLike
from ally.core.api.type import Iter
from newscoop.api.publication import Publication

# --------------------------------------------------------------------

@model()
class Issue(Entity):
    '''
    Provides the issue model.
    '''
    Name = str
    Number = str
    Description = str

# --------------------------------------------------------------------

@query(Issue)
class QIssue(QEntity):
    '''
    Provides the section query model.
    '''
    name = AsLike
    number = AsLike

# --------------------------------------------------------------------

@service(Issue)
class IIssueService(IEntityService):
    '''
    Provides services for issue.
    '''
    
    @call(Iter(Issue), Publication.Id, int, int, QIssue)
    def forPublication(self, publicationId, offset=None, limit=None, q=None):
        '''
        Provides all the issues that belong to the publication.
        
        @param publicationId: integer
            The publication if to retrieve the issues from.
        @param offset: integer
            The offset to retrieve the issues from.
        @param limit: integer
            The limit of sections to retrieve.
        @param q: QIssue
            The query to search by.
        '''
