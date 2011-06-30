'''
Created on Jun 8, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for publication.
'''

from newscoop.api.entity import Entity, IEntityService, QEntity
from ally.core.api.configure import APIModel as model, APIService as service, \
    APIQuery as query
from ally.core.api.criteria import AsLike

# --------------------------------------------------------------------

@model()
class Publication(Entity):
    '''
    Provides the publication model.
    '''
    name = str
    
# --------------------------------------------------------------------

@query(Publication)
class QPublication(QEntity):
    '''
    Provides the publication query model.
    '''
    name = AsLike

# --------------------------------------------------------------------

@service(Publication)
class IPublicationService(IEntityService):
    '''
    Provides services for publication.
    '''
