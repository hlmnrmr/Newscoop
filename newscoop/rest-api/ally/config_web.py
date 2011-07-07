'''
Created on Jul 2, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the web server.
'''

# --------------------------------------------------------------------

from ally import web
from ally.core.impl import assembler
from ally.core.impl.converter import Standard
from ally.core.impl.encdec_params import EncDecPrimitives, EncDecQuery
from ally.core.impl.encoder import EncoderXMLFactory
from ally.core.impl.processor.encoding import EncodingHandler
from ally.core.impl.processor.explain_error import ExplainErrorHandler
from ally.core.impl.processor.hinting import HintingHandler
from ally.core.impl.processor.invoking import InvokingHandler
from ally.core.impl.processor.parameters import ParametersHandler
from ally.core.impl.processor.rendering import RenderingHandler
from ally.core.impl.processor.uri import URIHandler
from ally.core.impl.render import RenderListPath, RenderListIds, RenderModel, \
    RenderListModels
from ally.core.impl.resources_manager import ResourcesManagerImpl
from ally.core.spec.presenting import Renders
from ally.core.spec.server import Processors
from ally.core.util import initialize, IoCResources

# --------------------------------------------------------------------

services = None
# To be injected before setup, provides the services to be used by the server.
location = None
# To be injected before setup, provides the location of the server.
port = None
# To be injected before setup, provides the port of the server.
serviceConfigModule = None
# The service configuration module 

# ------------------------------------------------------------------------

def setup(rsc):
    assert isinstance(rsc, IoCResources)
    # --------------------------------------------------------------------
    #  Creating the resource manager
    resourcesManager = ResourcesManagerImpl()
    resourcesManager.assemblers = [assembler.AssembleGetAll(), assembler.AssembleGetById(),
                                   assembler.AssembleInsert(), assembler.AssembleUpdateIdModel(),
                                   assembler.AssembleUpdateModel(), assembler.AssembleDelete()]
    
    # --------------------------------------------------------------------
    # Creating the resource manager
    if serviceConfigModule is None:
        raise AssertionError('No services configuration module provided, set on "config_web.serviceConfigModule"' + \
                             ' the configuration module that provides the services')
    serviceConfigModule.setup(rsc.add(**locals()))
    resourcesManager.services = rsc['services']
    initialize(resourcesManager)
    
    # --------------------------------------------------------------------
    # Creating the converters
    converterPath = Standard()
    initialize(converterPath)
    
    converterContent = Standard()
    initialize(converterContent)
    
    # --------------------------------------------------------------------
    # Creating the parameters encoders and decoders
    encDecPrimitives = EncDecPrimitives()
    encDecPrimitives.converter = converterPath
    initialize(encDecPrimitives)
    
    encDecQuery = EncDecQuery()
    encDecQuery.converter = converterPath
    initialize(encDecQuery)
    
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
    
    renderListModels = RenderListModels()
    initialize(renderListModels)
    
    renderModel = RenderModel()
    renderModel.resourcesManager = resourcesManager
    initialize(renderModel)
    
    renders = Renders()
    renders.renders = [renderListPath, renderListIds, renderListModels, renderModel]
    
    # --------------------------------------------------------------------
    # Creating the processors used in handling the request
    uri = URIHandler()
    uri.resourcesManager = resourcesManager
    uri.converter = converterPath
    if location is None:
        raise AssertionError('No location provided, set on "config_web.location" the server location')
    if port is None: raise AssertionError('No port provided, set on "config_web.port" the port value')
    uri.netloc = location + (':' + port if port != 80 else '')
    initialize(uri)
    
    explainErrorHandler = ExplainErrorHandler()
    initialize(explainErrorHandler)
    
    parameters = ParametersHandler()
    parameters.decoders = [encDecPrimitives, encDecQuery]
    initialize(parameters)
    
    hintingHandler = HintingHandler()
    hintingHandler.encoders = [encDecPrimitives, encDecQuery]
    initialize(hintingHandler)
    
    invokingHandler = InvokingHandler()
    initialize(invokingHandler)
    
    encoding = EncodingHandler()
    encoding.defaultEncoderFactory = encodingDefault
    encoding.encoderFactories = encodingFactories
    initialize(encoding)
    
    renderingHandler = RenderingHandler()
    renderingHandler.renders = renders
    initialize(renderingHandler)
    
    processors = [explainErrorHandler, uri, parameters, rsc['sessionOpen'], invokingHandler,
                  parameters, encoding, renderingHandler, rsc['sessionClose']]
    
    # --------------------------------------------------------------------
    # Creating the server processors container
    serverProcessors = Processors()
    serverProcessors.processors = processors
    initialize(serverProcessors)
    
    web.RequestHandler.processors = serverProcessors
    web.port = port
    
    # --------------------------------------------------------------------

    rsc.add(**locals())
