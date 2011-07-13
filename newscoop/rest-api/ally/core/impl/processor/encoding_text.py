'''
Created on Jul 12, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text encoding base handler.
'''

from _pyio import TextIOWrapper
from ally.core.api.type import Iter, TypeProperty, TypeId, TypeModel
from ally.core.spec.resources import Path, ResourcesManager, Converter
from ally.core.spec.server import Processor, ProcessorsChain, Response, Request
from ally.core.util import injected
import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------
    
@injected
class EncodingTextBaseHandler(Processor):
    '''
    Provides a basic class for encoders that are text based.
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
    
    def __init__(self, contentType):
        assert isinstance(contentType, str), 'Invalid content type %s' % contentType
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        assert isinstance(self.converter, Converter), 'Invalid Converter object %s' % self.converter
        assert isinstance(self.tagResources, str), 'Invalid string %s' % self.tagResources
        assert isinstance(self.tagListSufix, str), 'Invalid string %s' % self.tagListSufix
        assert isinstance(self.attrPath, str), 'Invalid string %s' % self.attrPath
        self.contentType = contentType
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if rsp.contentType == self.contentType:
            txt = TextIOWrapper(rsp.dispatch(), rsp.charSet, 'strict')
            # Need to stop the text close since this will close the socket, just a small hack to prevent this.
            txt.close = None
            out = self._createEncoder(txt, rsp.charSet)
            typ = req.objType
            if isinstance(typ, Iter):
                assert isinstance(typ, Iter)
                if typ.forClass() == Path:
                    self._renderListPath(out, req.obj, rsp.encoderPath)
                elif isinstance(typ.itemType, TypeProperty) and isinstance(typ.itemType.property.type, TypeId):
                    self._renderListIds(out, req.obj, typ.itemType, rsp.encoderPath)
                elif isinstance(typ.itemType, TypeModel):
                    self._renderListModels(out, req.obj, typ.itemType.model)
                else:
                    raise AssertionError('Cannot encode list item object type %s' % typ.itemType)
            elif isinstance(typ, TypeModel):
                self._renderModel(out, req.obj, typ.model)
            else:
                raise AssertionError('Cannot encode object type %s' % typ)
            log.debug('Encoded to %s using character set %s', rsp.contentType, rsp.charSet)
            self._endEncoding(out)
        else:
            chain.process(req, rsp)
        
    # --------------------------------------------------------------------
    
    @abc.abstractclassmethod
    def _createEncoder(self, textStream, charSet):
        '''
        Create the encoder for this processor.
        '''
        
    def _endEncoding(self, out):
        '''
        Called after the encoding ends.
        '''
        
    # --------------------------------------------------------------------

    @abc.abstractclassmethod
    def _renderListPath(self, out, paths, pencoder):
        '''
        Render a list of path elements.
        '''
    
    @abc.abstractclassmethod
    def _renderListIds(self, out, ids, typProp, pencoder):
        '''
        Render a list of id's.
        '''
    
    @abc.abstractclassmethod
    def _renderModel(self, out, obj, model):
        '''
        Render a model.
        '''
    
    @abc.abstractclassmethod
    def _renderListModels(self, out, objects, model):
        '''
        Render a list of models.
        '''
