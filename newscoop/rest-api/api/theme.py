'''
Created on Jun 8, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

API specifications for themes.
'''

from newscoop.api.entity import Entity, IEntityService, QEntity
from newscoop.core.api.configure import APIModel as model, APIService as service, \
    APIQuery as query, APICall as call
from newscoop.core.api.criteria import AsLike
from newscoop.core.api.type import List
from newscoop.api.resource import Resource
from newscoop.api.publication import Publication

# --------------------------------------------------------------------

@model()
class Theme(Entity):
    '''
    Provides the theme model.
    '''
    name = str
    designer = str
    version = str
    minorNewscoopVersion = str
    description = str
    publication = Publication.id
    frontImage = Resource.id
    sectionImage = Resource.id
    articleImage = Resource.id

# --------------------------------------------------------------------
  
@query(Theme)
class QTheme(QEntity):
    '''
    Provides the theme query model.
    '''
    name = AsLike
    designer = AsLike
    version = AsLike
    minorNewscoopVersion = AsLike
    description = AsLike
    
    def __init__(self): pass #Just to have proper type hinting for criteria

# --------------------------------------------------------------------

@service(Theme)
class IThemeService(IEntityService):
    '''
    Provides the theme service.
    '''
    
    @call(List(Theme.id), Publication.id, QTheme)
    def forPublication(self, pubId, q=None):
        '''
        Provides the themes for the publication searched by the provided query.
#        '''
#        
#    @call(List(Theme.id), QTheme)
#    def unassigned(self, q=None):
#        '''
#        Provides the unassigned themes searched by the provided query.
#        '''
#    
#    @call(List(Resource.id), Theme.id)
#    def templates(self, id):
#        '''
#        Provides the all template resources found for the theme.
#        '''
