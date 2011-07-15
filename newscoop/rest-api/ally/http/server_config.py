'''
Created on Jul 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the web server.
'''

from ally.core.impl import assembler as ass, encdec_param as edp
from ally.core.impl.converter import Standard
from ally.core.impl.processor.encoding import EncodingProcessorsHandler
from ally.core.impl.processor.encdec_json import EncodingJSONHandler, \
    DecodingJSONHandler
from ally.core.impl.processor.encdec_xml import EncodingXMLHandler, \
    DecodingXMLHandler
from ally.core.impl.processor.explain_error import ExplainErrorHandler
from ally.core.impl.processor.hinting import HintingHandler
from ally.core.impl.processor.invoking import InvokingHandler
from ally.core.impl.processor.parameters import ParametersHandler
from ally.core.impl.resources_manager import ResourcesManagerImpl
from ally.core.spec import charset as cs, content_type as ct
from ally.core.spec.server import Processors
from ally.core.util import initialize
from ally.http import encdec_header as edh
from ally.http.processor.content import ContentHandler
from ally.http.processor.decoding_header import DecodingHeaderHandler
from ally.http.processor.uri import URIHandler
from ally.http.server import RequestHandler
from ally.core.impl.processor.method_validation import MethodValidationHandler
from ally.core.impl.processor.decoding import DecodingHandler
from ally.core.impl.assembler import AssembleGetAllByOther

# --------------------------------------------------------------------

__version__ = '0.1'

specificationEngine = None
# The engine to use by the decoders.
serverLocation = None
# To be injected before setup, provides the location of the server.
serverPort = None
# To be injected before setup, provides the port of the server.
services = None
# To be injected before setup, provides the services to be used by the server.

# --------------------------------------------------------------------
# The configurations for content type and character sets.
contentTypes = {
                ct.XML:['text/xml', 'text/plain', 'application/xml', 'xml'],
                ct.JSON:['text/json', 'application/json', 'json']
                }

charSets = {
            cs.UTF_8:[cs.UTF_8, cs.UTF_8.lower()],
            cs.ISO_1:[cs.ISO_1, cs.ISO_1.lower()]
            }

# --------------------------------------------------------------------
# Creating the converters

converterPath = Standard()
converterContent = Standard()

def setupConverters():
    initialize(converterPath)
    
    initialize(converterContent)

# --------------------------------------------------------------------
# Creating the header encoders and decoders

parserContentType = encPsrContentType = edh.EncPsrContentType()
parserContentLength = edh.ParserContentLength()

encoderAllow = edh.EncoderAllow()
encoderContentLocation = edh.EncoderContentLocation()

decoderAcceptContentType = edh.DecoderAcceptContentType()
decoderAcceptCharSet = edh.DecoderAcceptCharSet()
# ---------------------------------
encodersHeader = [encPsrContentType, encoderAllow, encoderContentLocation]
decodersHeader = [decoderAcceptContentType, decoderAcceptCharSet]

def setupHeaders():
    encPsrContentType.contentTypes = contentTypes
    encPsrContentType.charSets = charSets
    initialize(encPsrContentType)
   
    initialize(parserContentLength)
    
    initialize(encoderAllow)
    
    encoderContentLocation.resourcesManager = resourcesManager
    initialize(encoderContentLocation)
    
    decoderAcceptContentType.contentTypes = contentTypes
    initialize(decoderAcceptContentType)
    
    decoderAcceptCharSet.charSets = charSets
    initialize(decoderAcceptCharSet)

# --------------------------------------------------------------------
# Creating the parameters encoders and decoders

encDecPrimitives = edp.EncDecPrimitives()
encDecQuery = edp.EncDecQuery()
# ---------------------------------
encodersParameters = [encDecPrimitives, encDecQuery]
decodersParameters = [encDecPrimitives, encDecQuery]

def setupParameters():
    encDecPrimitives.converter = converterPath
    initialize(encDecPrimitives)
    
    encDecQuery.converter = converterPath
    initialize(encDecQuery)

# --------------------------------------------------------------------
# Creating the assemblers

assembleGetAll = ass.AssembleGetAll()
assembleGetById = ass.AssembleGetById()
assembleInsert = ass.AssembleInsert()
assembleUpdateIdModel = ass.AssembleUpdateIdModel()
assembleUpdateModel = ass.AssembleUpdateModel()
assembleDelete = ass.AssembleDelete()
assembleGetAllByOther = AssembleGetAllByOther()
# ---------------------------------
assemblers = [assembleGetAll, assembleGetById, assembleInsert, assembleUpdateIdModel, assembleUpdateModel,
              assembleDelete, assembleGetAllByOther]

def setupAssemblers():
    initialize(assembleGetAll)
    initialize(assembleGetById)
    initialize(assembleInsert)
    initialize(assembleUpdateIdModel)
    initialize(assembleUpdateModel)
    initialize(assembleDelete)
    initialize(assembleGetAllByOther)

# --------------------------------------------------------------------
# Creating the encoding processors

resourcesManager = ResourcesManagerImpl()

def setupResourcesManager():
    if services is None: raise AssertionError('Set on "services" the services to be used')
    
    resourcesManager.assemblers = assemblers
    resourcesManager.services = services
    initialize(resourcesManager)

# --------------------------------------------------------------------
# Creating the encoding processors

encodingXML = EncodingXMLHandler()
encodingJSON = EncodingJSONHandler()
# ---------------------------------
handlersEncoding = [encodingXML, encodingJSON]
processorsEncoding = Processors()

def setupProcessorsEncoding():
    encodingXML.converter = converterContent
    encodingXML.resourcesManager = resourcesManager
    initialize(encodingXML)
    
    encodingJSON.converter = converterContent
    encodingJSON.resourcesManager = resourcesManager
    initialize(encodingJSON)
    
    processorsEncoding.processors = handlersEncoding
    initialize(processorsEncoding)

# --------------------------------------------------------------------
# Creating the decoding processors

decodingXML = DecodingXMLHandler()
decodingJSON = DecodingJSONHandler()
# ---------------------------------
handlersDecoding = [decodingXML, decodingJSON]
processorsDecoding = Processors()

def setupProcessorsDecoding():
    decodingXML.converter = converterContent
    decodingXML.specificationEngine = specificationEngine
    initialize(decodingXML)
    
    decodingJSON.converter = converterContent
    decodingJSON.specificationEngine = specificationEngine
    initialize(decodingJSON)
    
    processorsDecoding.processors = handlersDecoding
    initialize(processorsDecoding)
    
# --------------------------------------------------------------------
# Creating the processors used in handling the request

explainErrorHandler = ExplainErrorHandler()
decodingHeaderHandler = DecodingHeaderHandler()
contentHandler = ContentHandler()
uri = URIHandler()
methodValidation = MethodValidationHandler()
parameters = ParametersHandler()
invokingHandler = InvokingHandler()
hintingHandler = HintingHandler()
encoding = EncodingProcessorsHandler()
decoding = DecodingHandler()
# ---------------------------------
handlers = [explainErrorHandler, decodingHeaderHandler, contentHandler, uri, methodValidation, parameters, \
                  decoding, invokingHandler, hintingHandler, encoding]
processors = Processors()

def setupProcessors():
    if serverLocation is None:
        raise AssertionError('Set on "serverLocation" the server location something like "localhost"')
    if serverPort is None: raise AssertionError('Set on "serverPort" the port value something like 80')

    initialize(explainErrorHandler)
    
    decodingHeaderHandler.decoders = decodersHeader
    initialize(decodingHeaderHandler)
    
    contentHandler.parserContentLength = parserContentLength
    contentHandler.parserContentType = parserContentType
    initialize(contentHandler)

    uri.contentTypes = contentTypes
    uri.resourcesManager = resourcesManager
    uri.converter = converterPath
    uri.netloc = serverLocation + (':' + str(serverPort) if serverPort != 80 else '')
    initialize(uri)
    
    initialize(methodValidation)
    
    parameters.decoders = decodersParameters
    initialize(parameters)
    
    decoding.decodings = processorsDecoding
    initialize(decoding)
    
    invokingHandler.resourcesManager = resourcesManager
    initialize(invokingHandler)
    
    hintingHandler.encoders = encodersParameters
    initialize(hintingHandler)
    
    encoding.encodings = processorsEncoding
    initialize(encoding)
    
    processors.processors = handlers
    initialize(processors)
    
    RequestHandler.processors = processors
    RequestHandler.encodersHeader = encodersHeader
    RequestHandler.server_version = 'AllyREST/' + __version__

# --------------------------------------------------------------------

def setupAll():
    setupConverters()
    setupHeaders()
    setupParameters()
    setupAssemblers()
    setupResourcesManager()
    setupProcessorsEncoding()
    setupProcessorsDecoding()
    setupProcessors()
