'''
Created on Jul 2, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the web server.
'''

# --------------------------------------------------------------------
import logging
from ally.core.impl.processor.parameters import ParametersHandler
from ally.core.impl.processor.explain_error import ExplainErrorHandler

logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARN)
from ally.core import util
util.GUARD_ENABLED = __debug__
# --------------------------------------------------------------------

from ally.core.util import initialize
from ally.core.impl import assembler
from ally.core.impl.converter import Standard
from ally.core.impl.encoder import EncoderXMLFactory
from ally.core.impl.processor.encoding import EncodingHandler
from ally.core.impl.processor.invoking import InvokingHandler
from ally.core.impl.processor.rendering import RenderingHandler
from ally.core.impl.processor.uri import URIHandler
from ally.core.impl.render import RenderListPath, RenderListIds, RenderModel
from ally.core.impl.resources_manager import ResourcesManagerImpl
from ally.core.spec.presenting import Renders
from ally.core.spec.server import Processors

# --------------------------------------------------------------------
#  Creating the resource manager
resourcesManager = ResourcesManagerImpl()
resourcesManager.assemblers = [assembler.AssembleGetAll(), assembler.AssembleGetById()]

# --------------------------------------------------------------------
# Creating the resource manager
from ally import config_service
resourcesManager.services = config_service.services
initialize(resourcesManager)

# --------------------------------------------------------------------
# Creating the converters
converterPath = Standard()
initialize(converterPath)

converterContent = Standard()
initialize(converterContent)

# --------------------------------------------------------------------
# Creating the encodings
encodingXML = EncoderXMLFactory()
encodingXML.converter = converterContent
initialize(encodingXML)

encodingFactories = [encodingXML]
encodingDefault = encodingXML

# --------------------------------------------------------------------
# Creating the renders
renderListPath = RenderListPath()
initialize(renderListPath)

renderListIds = RenderListIds()
renderListIds.resourcesManager = resourcesManager
initialize(renderListIds)

renderModel = RenderModel()
renderModel.resourcesManager = resourcesManager
initialize(renderModel)

renders = Renders()
renders.renders = [renderListPath, renderListIds, renderModel]

# --------------------------------------------------------------------
# Creating the processors used in handling the request
uri = URIHandler()
uri.resourcesManager = resourcesManager
uri.converter = converterPath
uri.domain = 'http://localhost/'
initialize(uri)

explerrhand = ExplainErrorHandler()
initialize(explerrhand)

parameters = ParametersHandler()
parameters.converter = converterPath
initialize(parameters)

invokingHandler = InvokingHandler()
initialize(invokingHandler)

encoding = EncodingHandler()
encoding.defaultEncoderFactory = encodingDefault
encoding.encoderFactories = encodingFactories
initialize(encoding)

renderingHandler = RenderingHandler()
renderingHandler.renders = renders
initialize(renderingHandler)

processors = [explerrhand, uri, parameters, invokingHandler, encoding, renderingHandler]

# --------------------------------------------------------------------
# Creating the server processors container
serverProcessors = Processors()
serverProcessors.processors = processors
initialize(serverProcessors)

# --------------------------------------------------------------------

