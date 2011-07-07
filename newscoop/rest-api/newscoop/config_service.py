'''
Created on Jul 3, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the services.
'''
from ally.core.tools.dummy import ServiceDummy
from newscoop.api import resource, theme

from newscoop.impl_alchemy.publication import PublicationServiceAlchemy
from ally.core.util import initialize, IoCResources
from newscoop.impl_alchemy import AlchemyOpenSessionHandler, \
    AlchemyCloseSessionHandler

def setup(rsc):
    assert isinstance(rsc, IoCResources)
    resourcesManager = rsc['resourcesManager']
    # --------------------------------------------------------------------
    # Creating the SQL Alchemy session processors
    
    sessionOpen = AlchemyOpenSessionHandler()
    sessionOpen.engine = rsc['engine']
    initialize(sessionOpen)
    
    sessionClose = AlchemyCloseSessionHandler()
    
    # --------------------------------------------------------------------
    # Creating the services
    resourceService = ServiceDummy(resource.IResourceService)
    resourceService.resourcesManager = resourcesManager
    initialize(resourceService)
    
    publicationService = PublicationServiceAlchemy()
    initialize(publicationService)
    
    themeService = ServiceDummy(theme.IThemeService)
    themeService.resourcesManager = resourcesManager
    initialize(themeService)
    
    services = [resourceService, publicationService, themeService]
    
    # --------------------------------------------------------------------
    
    rsc.add(**locals())
