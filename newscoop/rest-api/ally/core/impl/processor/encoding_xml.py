'''
Created on Jul 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the XML encoding handler.
'''

from ally.core.api.operator import Model, Property
from ally.core.api.type import TypeProperty, typeFor
from ally.core.impl.node import NodeModel
from ally.core.impl.processor.encoding_text import EncodingTextBaseHandler
from ally.core.spec import content_type as ct
from ally.core.spec import charset as cs
from ally.core.spec.presenting import EncoderPath
from ally.core.spec.resources import Path
from xml.sax.saxutils import XMLGenerator
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain, \
    INSERT, UPDATE, Content
from ally.core.util import injected
from xml.parsers.expat import ParserCreate
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from xml.sax.xmlreader import InputSource

# --------------------------------------------------------------------

class EncodingXMLHandler(EncodingTextBaseHandler):
    '''
    Provides the XML encoding.
    '''
    
    def __init__(self):
        super().__init__(ct.XML)
    
    # --------------------------------------------------------------------
    
    def _createEncoder(self, textStream, charSet):
        '''
        @see: EncodingTextBaseHandler._createEncoder
        '''
        xml = XMLGenerator(textStream, charSet)
        xml.startDocument()
        return xml
    
    def _endEncoding(self, xml):
        '''
        @see: EncodingTextBaseHandler._endEncoding
        '''
        xml.endDocument()
    
    # --------------------------------------------------------------------

    def _renderListPath(self, xml, paths, pencoder):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(pencoder, EncoderPath)
        xml.startElement(self.tagResources, {})
        for path in paths:
            assert isinstance(path, Path), 'Invalid path %s' % path
            node = path.node
            if isinstance(node, NodeModel):
                assert isinstance(node, NodeModel)
                xml.startElement(node.model.name, {self.attrPath:pencoder.encode(path)})
                xml.endElement(node.model.name)
        xml.endElement(self.tagResources)
    
    def _renderListIds(self, xml, ids, typProp, pencoder):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(pencoder, EncoderPath)
        assert isinstance(typProp, TypeProperty)
        listName = typProp.model.name + self.tagListSufix
        xml.startElement(listName, {})
        path = self.resourcesManager.findShortPath(typeFor(typProp.model.modelClass), typProp)
        for id in ids:
            if path is None:
                attrs = {}
            else:
                assert isinstance(path, Path)
                path.update(id, typProp)
                attrs = {self.attrPath:pencoder.encode(path)}
            xml.startElement(typProp.property.name, attrs)
            xml.characters(self.converter.asString(id))
            xml.endElement(typProp.property.name)
        xml.endElement(listName)
        
    def _renderModel(self, xml, obj, model):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(model, Model)
        xml.startElement(model.name, {})
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            value = prop.get(obj)
            if value is not None:
                xml.startElement(prop.name, {})
                xml.characters(self.converter.asString(value))
                xml.endElement(prop.name)
        xml.endElement(model.name)
        
    def _renderListModels(self, xml, objects, model):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(model, Model)
        listName = model.name + self.tagListSufix
        xml.startElement(listName, {})
        for obj in objects:
            self._renderModel(xml, obj, model)
        xml.endElement(listName)


# --------------------------------------------------------------------
    
@injected
class DecodingXMLHandler(Processor):
    '''
    Provides a basic class for encoders that are text based.
    '''
    
    charSetDefault = cs.ISO_1
    # The default character set to be used if none provided for the content.
    
    def __init__(self):
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if req.method in (INSERT, UPDATE):
            cnt = req.content
            assert isinstance(cnt, Content)
            if cnt.contentType == ct.XML:
                charSet = rsp.charSet or self.charSetDefault
                parser = make_parser()
                parser.setContentHandler(XMLHandler())
                inpSrc = InputSource()
                inpSrc.setByteStream(req.content)
                inpSrc.setEncoding(charSet)
                parser.parse(inpSrc)
                 
        chain.process(req, rsp)

class XMLHandler(ContentHandler):
    '''
    Provides the XML parsing handling.
    '''
    
    def startElement(self, name, attributes):
        '''
        @see: ContentHandler.startElement
        '''
        print('START----->', name, attributes)
 
    def characters(self, data):
        '''
        @see: ContentHandler.characters
        '''
        print('CHARS----->', data)
 
    def endElement(self, name):
        '''
        @see: ContentHandler.endElement
        '''
        print('END----->', name)
