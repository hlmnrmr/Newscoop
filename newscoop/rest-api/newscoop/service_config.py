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
from ally.core.support.sql_alchemy import AlchemySessionHandler
from ally.http import server_config
from ally.core.util import initialize
from newscoop import php_client_config
from newscoop.impl_alchemy.section import SectionServiceAlchemy
from newscoop.impl_alchemy.issue import IssueServiceAlchemy

# --------------------------------------------------------------------

engine = None
# To be injected before setup, provides the SQL alchemy database engine.

# --------------------------------------------------------------------

handlers = server_config.handlers
invokingHandler = server_config.invokingHandler
resourcesManager = server_config.resourcesManager

# --------------------------------------------------------------------
# Creating the SQL Alchemy session processors

alchemySessionHandler = AlchemySessionHandler()
# ---------------------------------
k = handlers.index(invokingHandler)
handlers.insert(k, alchemySessionHandler)

def setupProcessors():
    if engine is None: raise AssertionError('Set on "engine" the SQL Alchemy database engine')
    
    alchemySessionHandler.engine = engine
    initialize(alchemySessionHandler)

# --------------------------------------------------------------------
# Creating the services

resourceService = ServiceDummy(resource.IResourceService)
themeService = ServiceDummy(theme.IThemeService)
publicationService = PublicationServiceAlchemy()
sectionService = SectionServiceAlchemy()
issueService = IssueServiceAlchemy()

# ---------------------------------
server_config.services = [resourceService, publicationService, sectionService, themeService, issueService]

def setupServices():
    resourceService.resourcesManager = resourcesManager
    initialize(resourceService)
    
    initialize(publicationService)
    
    initialize(sectionService)
    
    initialize(issueService)
    
    themeService.resourcesManager = resourcesManager
    initialize(themeService)
    
# --------------------------------------------------------------------

def setupAll():
    setupProcessors()
    setupServices()
    server_config.setupAll()
    php_client_config.setupAll()
