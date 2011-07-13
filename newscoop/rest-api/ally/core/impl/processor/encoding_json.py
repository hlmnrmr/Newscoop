'''
Created on Jul 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the JSON encoding handler.
'''

from _pyio import TextIOWrapper
from ally.core.api.operator import Model, Property
from ally.core.api.type import TypeProperty, typeFor
from ally.core.impl.node import NodeModel
from ally.core.impl.processor.encoding_text import EncodingTextBaseHandler
from ally.core.spec import content_type as ct
from ally.core.spec.presenting import EncoderPath
from ally.core.spec.resources import Path
from numbers import Number
import json

# --------------------------------------------------------------------

class EncodingJSONHandler(EncodingTextBaseHandler):
    '''
    Provides the JSON encoding.
    '''
    
    def __init__(self):
        super().__init__(ct.JSON)
        
    def _createEncoder(self, textStream, charSet):
        '''
        @see: EncodingTextBaseHandler._createEncoder
        '''
        return textStream
    
    # --------------------------------------------------------------------

    def _renderListPath(self, txt, paths, pencoder):
        assert isinstance(txt, TextIOWrapper)
        assert isinstance(pencoder, EncoderPath)
        txt.write('{')
        json.dump(self.tagResources, txt)
        txt.write(':{')
        first = True
        for path in paths:
            assert isinstance(path, Path), 'Invalid path %s' % path
            node = path.node
            if isinstance(node, NodeModel):
                assert isinstance(node, NodeModel)
                if not first:
                    txt.write(',')
                first = False
                json.dump(node.model.name, txt)
                txt.write(':')
                json.dump({self.attrPath:pencoder.encode(path)}, txt)
        txt.write('}}')
    
    def _renderListIds(self, txt, ids, typProp, pencoder):
        assert isinstance(txt, TextIOWrapper)
        assert isinstance(pencoder, EncoderPath)
        assert isinstance(typProp, TypeProperty)
        txt.write('{')
        json.dump(typProp.model.name + self.tagListSufix, txt)
        txt.write(':[')
        path = self.resourcesManager.findShortPath(typeFor(typProp.model.modelClass), typProp)
        first = True
        for id in ids:
            if not first:
                txt.write(',')
            first = False
            txt.write('{')
            json.dump(typProp.property.name, txt)
            txt.write(':')
            txt.write(self.converter.asString(id))
            if path is not None:
                assert isinstance(path, Path)
                path.update(id, typProp)
                txt.write(',')
                json.dump(self.attrPath, txt)
                txt.write(':')
                json.dump(pencoder.encode(path), txt)
            txt.write('}')
        txt.write(']}')
        
    def _renderModel(self, txt, obj, model):
        assert isinstance(txt, TextIOWrapper)
        assert isinstance(model, Model)
        txt.write('{')
        json.dump(model.name, txt)
        txt.write(':{')
        first = True
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            value = prop.get(obj)
            if value is not None:
                if not first:
                    txt.write(',')
                first = False
                json.dump(prop.name, txt)
                txt.write(':')
                if isinstance(value, Number):
                    txt.write(self.converter.asString(value))
                else:
                    json.dump(self.converter.asString(value), txt)
        txt.write('}}')
        
    def _renderListModels(self, txt, objects, model):
        assert isinstance(txt, TextIOWrapper)
        assert isinstance(model, Model)
        txt.write('{')
        json.dump(model.name + self.tagListSufix, txt)
        txt.write(':[')
        first = True
        for obj in objects:
            if not first:
                txt.write(',')
            first = False
            self._renderModel(txt, obj, model)
        txt.write(']}')
