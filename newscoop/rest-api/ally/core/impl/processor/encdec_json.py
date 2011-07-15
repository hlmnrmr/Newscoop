'''
Created on Jul 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the JSON encoding handler.
'''

from _pyio import TextIOWrapper
from ally.core.api.exception import InputException
from ally.core.api.operator import Model, Property, PropertySepcification
from ally.core.api.type import TypeProperty, typeFor, Iter, isPropertyTypeId, \
    TypeModel, Input, isTypeId
from ally.core.impl.node import NodeModel
from ally.core.internationalization import msg as _
from ally.core.spec import charset as cs, content_type as ct
from ally.core.spec.codes import BAD_CONTENT
from ally.core.spec.presenting import EncoderPath
from ally.core.spec.resources import Path, Converter, ResourcesManager, Invoker
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain, \
    INSERT, UPDATE, Content
from ally.core.util import injected
import codecs
import json
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncodingJSONHandler(Processor):
    '''
    Provides the JSON encoding.
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the resource nodes for the id's presented.
    converter = Converter
    # The converter used by the encoders of this factory.
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
        if rsp.contentType == ct.JSON:
            typ = req.objType
            if typ is None:
                if rsp.contentLocation is not None:
                    obj = {self.converter.normalize(self.attrPath):rsp.encoderPath.encode(rsp.contentLocation)}
                else:
                    raise AssertionError('No object or content location to encode')
            elif isinstance(typ, Iter):
                assert isinstance(typ, Iter)
                if typ.forClass() == Path:
                    obj = self._ruleListPath(req.obj, rsp.encoderPath)
                elif isPropertyTypeId(typ.itemType):
                    obj = self._ruleListIds(req.obj, typ.itemType, rsp.encoderPath)
                elif isinstance(typ.itemType, TypeModel):
                    obj = self._ruleListModels(req.obj, typ.itemType.model)
                else:
                    raise AssertionError('Cannot encode list item object type %s' % typ.itemType)
            elif isPropertyTypeId(typ):
                path = self.resourcesManager.findShortPath(typeFor(typ.model.modelClass), typ)
                obj = self._ruleId(req.obj, path, typ, rsp.encoderPath)
            elif isinstance(typ, TypeModel):
                obj = self._ruleModel(req.obj, typ.model)
            else:
                raise AssertionError('Cannot encode object type %s' % typ)
            txt = TextIOWrapper(rsp.dispatch(), rsp.charSet, 'strict')
            # Need to stop the text close since this will close the socket, just a small hack to prevent this.
            txt.close = None
            json.dump(obj, txt)
            log.debug('Encoded to JSON using character set %s', rsp.charSet)
        else:
            chain.process(req, rsp)

    def _ruleListPath(self, paths, pencoder):
        assert isinstance(pencoder, EncoderPath)
        pathsObj = {}
        for path in paths:
            assert isinstance(path, Path), 'Invalid path %s' % path
            node = path.node
            if isinstance(node, NodeModel):
                assert isinstance(node, NodeModel)
                pathsObj[self.converter.normalize(node.model.name)] = {self.attrPath:pencoder.encode(path)}
        return {self.converter.normalize(self.tagResources):pathsObj}
    
    def _ruleId(self, id, path, typProp, pencoder):
        idObj = {self.converter.normalize(typProp.property.name):id}
        if path is not None:
            assert isinstance(path, Path)
            path.update(id, typProp)
            idObj[self.converter.normalize(self.attrPath)] = pencoder.encode(path)
        return idObj
            
    def _ruleListIds(self, ids, typProp, pencoder):
        assert isinstance(pencoder, EncoderPath)
        assert isinstance(typProp, TypeProperty)
        idsList = []
        path = self.resourcesManager.findShortPath(typeFor(typProp.model.modelClass), typProp)
        for id in ids:
            idsList.append(self._ruleId(id, path, typProp, pencoder))
        return {self.converter.normalize(typProp.model.name + self.tagListSufix):idsList}
        
    def _ruleModel(self, obj, model):
        assert isinstance(model, Model)
        modelObj = {}
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            value = prop.get(obj)
            if value is not None:
                modelObj[self.converter.normalize(prop.name)] = value
        return {self.converter.normalize(model.name):modelObj}
        
    def _ruleListModels(self, objects, model):
        assert isinstance(model, Model)
        modelsList = []
        for obj in objects:
            modelsList.append(self._ruleModel(obj, model))
        return {self.converter.normalize(model.name + self.tagListSufix):modelsList}

# --------------------------------------------------------------------

@injected
class DecodingJSONHandler(Processor):
    '''
    Provides the decoder for JSON content.
    '''
    
    converter = Converter
    # The converter used by the decoder.
    charSetDefault = cs.ISO_1
    # The default character set to be used if none provided for the content.
    specificationEngine = None
    # The name of the specification engine to be considered for additional validation by the decoder.
    
    def __init__(self):
        assert isinstance(self.converter, Converter), 'Invalid Converter object %s' % self.converter
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault
        assert self.specificationEngine is None or isinstance(self.specificationEngine, str), \
        'Invalid specification engine name %s, can be None' % self.specificationEngine
        
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
        if cnt.contentType == ct.JSON:
            if req.method == INSERT:
                invoker = req.resourcePath.node.insert
            else:
                invoker = req.resourcePath.node.update
            assert isinstance(invoker, Invoker)
            # Normally the last argument in the input list describes the expected input type.
            inp = invoker.inputs[-1]
            assert isinstance(inp, Input)
            charSet = rsp.charSet or self.charSetDefault
            try:
                obj = json.load(codecs.getreader(charSet)(req.content))
            except ValueError as e:
                rsp.setCode(BAD_CONTENT, _('Invalid JSON content'))
                log.warning('Problems converting content to JSON: %s', e)
                return
            if isinstance(inp.type, TypeModel):
                try:
                    req.arguments[inp.name] = self._decodeModel(obj, inp.type.model)
                except InputException as e:
                    assert isinstance(e, InputException)
                    rsp.setCode(BAD_CONTENT, e.message)
                    log.warning('Problems decoding content from JSON: %s', e.message.default)
            else:
                raise AssertionError('Cannot decode object input %s' % inp)
        else:
            chain.process(req, rsp)
            
    def _decodeModel(self, obj, model):
        assert isinstance(model, Model)
        objCount = 1
        modelName = self.converter.normalize(model.name)
        modelObj = obj.pop(modelName, None)
        if modelObj is None:
            raise InputException(_('Expected key ($1) for object count $2', modelName, objCount))
        if len(obj) > 0:
            raise InputException(_('Unknown keys ($1) for object count $2', \
                                   ', '.join(str(key) for key in obj.keys()), objCount))
        objCount += 1
        obj = modelObj
        mi = model.createModel()
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            if not isTypeId(prop.type):
                propName = self.converter.normalize(prop.name)
                spec = None
                if self.specificationEngine is not None:
                    spec = prop.sepcificationFor(self.specificationEngine)
                    if spec is not None:
                        assert isinstance(spec, PropertySepcification)
                if propName in obj:
                    value = obj.pop(propName)
                    if not prop.type.isValid(value):
                        raise InputException(_('Invalid value ($1) for ($2), expected type ($3) for ' + 
                        'object count $4', value, propName, prop.type, objCount))
                        log.warning('Problems setting property (%s) from JSON value %s', propName, value)
                    if spec is not None and not spec.isValidLength(value):
                        raise InputException(_('Expected a maximum length of $1 for ($2), at ' + 
                        'object count $3', spec.length, propName, objCount))
                    prop.set(mi, value)
                elif spec is not None and spec.isRequired:
                    raise InputException(_('Required a value for ($1) at object count $2', \
                                           propName, objCount))
        if len(obj) > 0:
            raise InputException(_('Unknown keys ($1)', ', '.join(str(key) for key in obj.keys())))
        return mi
