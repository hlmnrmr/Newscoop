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
from ally.config_application import resourcesManager
from newscoop.impl import publication
from ally.core.util import initialize

# --------------------------------------------------------------------
# Creating the services
resourceService = ServiceDummy(resource.IResourceService)
resourceService.resourcesManager = resourcesManager
initialize(resourceService)

publicationService = publication.PublicationServiceTest()
initialize(publicationService)

themeService = ServiceDummy(theme.IThemeService)
themeService.resourcesManager = resourcesManager
initialize(themeService)

services = [resourceService, publicationService, themeService]
