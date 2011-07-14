'''
Created on Jul 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the XML encoding handler.
'''

from _abcoll import Callable
from _pyio import TextIOWrapper
from ally.core.api.exception import InputException
from ally.core.api.operator import Model, Property
from ally.core.api.type import TypeProperty, typeFor, Iter, TypeModel, \
    isPropertyTypeId, Input, isTypeId
from ally.core.impl.node import NodeModel
from ally.core.internationalization import msg as _
from ally.core.spec import charset as cs, content_type as ct
from ally.core.spec.codes import BAD_CONTENT
from ally.core.spec.presenting import EncoderPath
from ally.core.spec.resources import Path, ResourcesManager, Converter, Invoker
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain, \
    INSERT, UPDATE, Content
from ally.core.util import injected, guard
from inspect import isclass
from xml.sax import make_parser
from xml.sax._exceptions import SAXParseException
from xml.sax.handler import ContentHandler
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import InputSource
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncodingXMLHandler(Processor):
    '''
    Provides the XML encoding.
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the resource nodes for the id's presented.
    converter = Converter
    # The converter used by the encoding.
    tagResources = 'Resources'
    # The tag to be used as the main container for the resources.
    tagListSufix = 'List'
    # Will be appended at the end of the model name when rendering the list tag containing the list items.
    attrPath = 'href'
    # The attribute name to use as the attribute in rendering the hyper link.

    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        assert isinstance(self.converter, Converter), 'Invalid Converter object %s' % self.converter
        assert isinstance(self.tagResources, str), 'Invalid string %s' % self.tagResources
        assert isinstance(self.tagListSufix, str), 'Invalid string %s' % self.tagListSufix
        assert isinstance(self.attrPath, str), 'Invalid string %s' % self.attrPath
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if rsp.contentType == ct.XML:
            txt = TextIOWrapper(rsp.dispatch(), rsp.charSet, 'strict')
            # Need to stop the text close since this will close the socket, just a small hack to prevent this.
            txt.close = None
            xml = XMLGenerator(txt, rsp.charSet, True)
            xml.startDocument()
            typ = req.objType
            if typ is None:
                if rsp.contentLocation is not None:
                    pathName = self.converter.normalize(self.attrPath)
                    xml.startElement(pathName, {})
                    xml.characters(rsp.encoderPath.encode(rsp.contentLocation))
                    xml.endElement(pathName)
                else:
                    raise AssertionError('No object or content location to encode')
            elif isinstance(typ, Iter):
                assert isinstance(typ, Iter)
                if typ.forClass() == Path:
                    self._encodeListPath(xml, req.obj, rsp.encoderPath)
                elif isPropertyTypeId(typ.itemType):
                    self._encodeListIds(xml, req.obj, typ.itemType, rsp.encoderPath)
                elif isinstance(typ.itemType, TypeModel):
                    self._encodeListModels(xml, req.obj, typ.itemType.model)
                else:
                    raise AssertionError('Cannot encode list item object type %s' % typ.itemType)
            elif isPropertyTypeId(typ):
                path = self.resourcesManager.findShortPath(typeFor(typ.model.modelClass), typ)
                self._encodeId(xml, req.obj, path, typ, rsp.encoderPath)
            elif isinstance(typ, TypeModel):
                self._encodeModel(xml, req.obj, typ.model)
            else:
                raise AssertionError('Cannot encode object type %s' % typ)
            log.debug('Encoded to XML using character set %s', rsp.charSet)
            xml.endDocument()
        else:
            chain.process(req, rsp)

    def _encodeListPath(self, xml, paths, pencoder):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(pencoder, EncoderPath)
        listName = self.converter.normalize(self.tagResources)
        xml.startElement(listName, {})
        for path in paths:
            assert isinstance(path, Path), 'Invalid path %s' % path
            node = path.node
            if isinstance(node, NodeModel):
                assert isinstance(node, NodeModel)
                pathName = self.converter.normalize(node.model.name)
                xml.startElement(pathName, {self.attrPath:pencoder.encode(path)})
                xml.endElement(pathName)
        xml.endElement(listName)
    
    def _encodeId(self, xml, id, path, typProp, pencoder):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(pencoder, EncoderPath)
        assert isinstance(typProp, TypeProperty)
        if path is None:
            attrs = {}
        else:
            assert isinstance(path, Path)
            path.update(id, typProp)
            attrs = {self.attrPath:pencoder.encode(path)}
            propName = self.converter.normalize(typProp.property.name)
        xml.startElement(propName, attrs)
        xml.characters(self.converter.asString(id))
        xml.endElement(propName)
        
    def _encodeListIds(self, xml, ids, typProp, pencoder):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(pencoder, EncoderPath)
        assert isinstance(typProp, TypeProperty)
        listName = self.converter.normalize(typProp.model.name + self.tagListSufix)
        xml.startElement(listName, {})
        path = self.resourcesManager.findShortPath(typeFor(typProp.model.modelClass), typProp)
        for id in ids:
            self._encodeId(xml, id, path, typProp, pencoder)
        xml.endElement(listName)
        
    def _encodeModel(self, xml, obj, model):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(model, Model)
        modelName = self.converter.normalize(model.name)
        xml.startElement(modelName, {})
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            value = prop.get(obj)
            if value is not None:
                propName = self.converter.normalize(prop.name)
                xml.startElement(propName, {})
                xml.characters(self.converter.asString(value))
                xml.endElement(propName)
        xml.endElement(modelName)
        
    def _encodeListModels(self, xml, objects, model):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(model, Model)
        listName = self.converter.normalize(model.name + self.tagListSufix)
        xml.startElement(listName, {})
        for obj in objects:
            self._encodeModel(xml, obj, model)
        xml.endElement(listName)


# --------------------------------------------------------------------
    
@injected
class DecodingXMLHandler(Processor):
    '''
    Provides the decoder for XML content.
    '''
    
    converter = Converter
    # The converter used by the decoder.
    charSetDefault = cs.ISO_1
    # The default character set to be used if none provided for the content.
    
    def __init__(self):
        assert isinstance(self.converter, Converter), 'Invalid Converter object %s' % self.converter
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert req.method in (INSERT, UPDATE), 'Invalid method %s for processor' % req.method
        cnt = req.content
        assert isinstance(cnt, Content)
        if cnt.contentType == ct.XML:
            if req.method == INSERT:
                invoker = req.resourcePath.node.insert
            else:
                invoker = req.resourcePath.node.update
            assert isinstance(invoker, Invoker)
            # Normally the last argument in the input list describes the expected input type.
            inp = invoker.inputs[-1]
            assert isinstance(inp, Input)
            charSet = rsp.charSet or self.charSetDefault
            if isinstance(inp.type, TypeModel):
                root = self._createModel(inp.type.model)
            else:
                raise AssertionError('Cannot decode object input %s' % inp)
            try:
                value = Digester(root).parse(charSet, cnt)
                req.arguments[inp.name] = value
                log.debug('Successfully decoded for input (%s) value %s', inp.name, value)
            except InputException as e:
                assert isinstance(e, InputException)
                rsp.setCode(BAD_CONTENT, e.message)
                log.warning('Problems decoding content from XML: %s', e.message.default)
        else:
            chain.process(req, rsp)
        
    def _createModel(self, model):
        assert isinstance(model, Model)
        root = RuleRoot()
        rmodel = root.addRule(RuleCreate(model.createModel), self.converter.normalize(model.name))
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            if not isTypeId(prop.type):
                rmodel.addRule(RuleSetContent(prop.set, prop.type.forClass(), self.converter), \
                               self.converter.normalize(prop.name))
        return root

# --------------------------------------------------------------------

@guard
class Digester(ContentHandler):
    '''
    Provides a digester for XML.
    '''
    
    def __init__(self, root):
        '''
        @param root: Node
            The root node.
        @ivar stack: list
            The stack that contains the values in the digester.
        '''
        assert isinstance(root, Node), 'Invalid root node %s' % root
        self.root = root
        self._nodes = [root]
        self.stack = []
        self._parser = make_parser()
        self._parser.setContentHandler(self)
    
    def parse(self, charSet, file):
        '''
        Parses the provided content.
        
        @param charSet: string
            The character set of the content.
        @param file: file type
            The file type object providing the content.
        @return: object
            The object obtained from parsing.
        '''
        inpsrc = InputSource()
        inpsrc.setByteStream(file)
        inpsrc.setEncoding(charSet)
        try:
            self._parser.parse(inpsrc)
        except SAXParseException as e:
            assert isinstance(e, SAXParseException)
            raise InputException(_('Bad XML content at line $1 and column $2', \
                                   e.getLineNumber(), e.getColumnNumber()))
        if len(self.stack) == 0:
            raise InputException(_('Invalid XML content provided'))
        return self.stack[0]
    
    def currentPath(self):
        '''
        Provides the current processing path of the digester.
        '''
        return '/'.join((self._nodes[i].path for i in range(1, len(self._nodes))))
    
    def startElement(self, path, attributes):
        '''
        @see: ContentHandler.startElement
        '''
        node = self._nodes[-1]
        assert isinstance(node, Node)
        if path not in node.childrens:
            raise InputException(_('Unknown path element ($1) in ($2) at line $3 and column $4',
                        path, self.currentPath(), self.getLineNumber(), self.getColumnNumber()))
        node = node.childrens[path]
        self._nodes.append(node)
        if len(attributes) > 0:
            raise InputException(_('No attributes accepted for path $1 at line $2 and column $3', \
                                   self.currentPath(), self.getLineNumber(), self.getColumnNumber()))
        for rule in node.rules:
            assert isinstance(rule, Rule)
            rule.begin(self)
 
    def characters(self, content):
        '''
        @see: ContentHandler.characters
        '''
        node = self._nodes[-1]
        assert isinstance(node, Node)
        for rule in node.rules:
            assert isinstance(rule, Rule)
            rule.content(self, content)
 
    def endElement(self, path):
        '''
        @see: ContentHandler.endElement
        '''
        node = self._nodes.pop()
        assert isinstance(node, Node)
        if not path == node.path:
            raise InputException(_('Unexpected end element ($1), expected ($2) at line $3 and column $4', \
                                   path, node.path, self.getLineNumber(), self.getColumnNumber()))
        for rule in node.rules:
            assert isinstance(rule, Rule)
            rule.end(self)
            
    def getLineNumber(self):
        return self._parser.getLineNumber()
    
    def getColumnNumber(self):
        return self._parser.getColumnNumber()

@guard
class Node:
    '''
    Defines a node of rules that contain the rule of the node and the childrens.
    '''
    
    def __init__(self, path):
        '''
        @param path: string
            The path element of the node.
        @ivar rules: list
            Contains the rules of the node.
        @ivar childrens: dictionary
            Contains all the children Nodes, as a key is the path element that describes the node.
        '''
        assert isinstance(path, str), 'Invalid node path %s' % path
        self.path = path
        self.rules = []
        self.childrens = {}
        
    def addRule(self, rule, *xpaths):
        '''
        Add a rule to this digester.
        
        @param rule: Rule
            The rule to be added.
        @param xpaths: tuple
            A tuple of string containing the xpath of the rule.
        @return: Node
            The node of the added rule.
        '''
        assert isinstance(rule, Rule), 'Invalid rule %s' % rule
        if __debug__:
            for path in xpaths:
                assert isinstance(path, str), 'Invalid path element %s' % path
        node = self.obtainNode(xpaths)
        node.rules.append(rule)
        return node
        
    def obtainNode(self, xpaths):
        '''
        Obtains the node for the specified xpaths list.
        
        @param xpaths: list
            The xpaths list to be searched.
        '''
        assert isinstance(xpaths, (list, tuple)), 'Invalid xpaths list %s' % xpaths
        for path, node in self.childrens.items():
            if path == xpaths[0]: break
        else:
            node = Node(xpaths[0])
            self.childrens[xpaths[0]] = node          
        if len(xpaths) > 1:
            return node.obtainNode(xpaths[1:])
        return node

class RuleRoot(Node):
    '''
    Provides a root node.
    '''
    
    def __init__(self):
        super().__init__('ROOT')

@guard
class Rule:
    '''
    Provides the parser rule base.
    '''
    
    def begin(self, digester):
        '''
        Called at element start.
        
        @param digester: Digester
            The processing digester.
        '''
    
    def content(self, digester, content):
        '''
        Called when the element has character data content.
        
        @param digester: Digester
            The processing digester.
        @param content: string
            The content of the element.
        '''
    
    def end(self, digester):
        '''
        Called at element end.
        
        @param digester: Digester
            The processing digester.
        '''

# --------------------------------------------------------------------

class RuleCreate(Rule):
    '''
    Rule implementation that provides the creation of an object at begin.
    '''
    
    def __init__(self, create):
        '''
        @param create: Callable
            The create Callable that will be used in creating the object, no arguments will be passed
            to this construct.
        '''
        assert isinstance(create, Callable), 'Invalid create callable %s' % create
        self._create = create
        
    def begin(self, digester):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, Digester)
        digester.stack.append(self._create())
        
    def end(self, digester):
        '''
        @see: Rule.end
        '''
        if len(digester.stack) > 1:
            digester.stack.pop()

# --------------------------------------------------------------------

class RuleSetContent(Rule):
    '''
    Rule implementation that sets the content of an element to the closest stack object.
    '''
    
    def __init__(self, setter, valueType, valueConverter):
        '''
        @param setter: Callable
            The callable to be used in setting the value, this will receive as the first argument the
            last stack object and as a second the value to set.
        @param valueType: type
            The type of the value to be set.
        @param valueConverter: Converter
            The converter to be used in transforming the content to the required value type.
        '''
        assert isinstance(setter, Callable), 'Invalid setter callable %s' % setter
        assert isclass(valueType), 'Invalid value type %s' % valueType
        assert isinstance(valueConverter, Converter), 'Invalid value converter %s' % valueConverter
        self._setter = setter
        self._valueType = valueType
        self._valueConverter = valueConverter
    
    def content(self, digester, content):
        '''
        @see: Rule.content
        '''
        assert isinstance(digester, Digester)
        assert len(digester.stack) > 0, \
        'Invalid structure there is no stack object to use for setting value on path %s' % digester.currentPath()
        try:
            value = self._valueConverter.asValue(content, self._valueType)
        except ValueError:
            raise InputException(_('Invalid value ($1) expected type $2 on path $3 at line $4 and column $5', \
            content, self._valueType, digester.currentPath(), digester.getLineNumber(), digester.getColumnNumber()))
        self._setter(digester.stack[-1], value)
