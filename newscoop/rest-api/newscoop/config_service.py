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
from newscoop.impl import tables_alchemy
from newscoop.impl.publication_alchemy import PublicationServiceAlchemy
from ally.core.util import initialize

def setup(**rsc):
    resourcesManager = rsc['resourcesManager']
    # --------------------------------------------------------------------
    # Creating the services
    resourceService = ServiceDummy(resource.IResourceService)
    resourceService.resourcesManager = resourcesManager
    initialize(resourceService)
    
    publicationService = PublicationServiceAlchemy()
    publicationService.db = tables_alchemy.db
    publicationService.table = tables_alchemy.tablePublication
    initialize(publicationService)
    
    themeService = ServiceDummy(theme.IThemeService)
    themeService.resourcesManager = resourcesManager
    initialize(themeService)
    
    services = [resourceService, publicationService, themeService]
    
    return locals()
