'''
Created on Jul 4, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides hints in the encoded paths.
'''

from ally.core.spec.presenting import EncoderPath, EncoderParams
from ally.core.spec.resources import Path, Node, Invoker
from ally.core.spec.server import Processor, ProcessorsChain, ResponseFormat
from ally.core.util import injected
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class HintingHandler(Processor):
    '''
    Implementation for a processor that provides hints in the response encoded paths.
    '''
    
    encoders = list
    # The parameters encoders used for adding parameters to the path.
   
    def __init__(self):
        if __debug__:
            for encoder in self.encoders:
                assert isinstance(encoder, EncoderParams), 'Invalid parameters encoder %s' % encoder
    
    def process(self, requestAny, responseFormat, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if isinstance(responseFormat, ResponseFormat):
            assert isinstance(responseFormat, ResponseFormat)
            hinter = EncoderPathHinter(responseFormat.encoderPath, self)
            responseHinter = ResponseFormat(responseFormat.response, hinter, responseFormat.format)
            chain.process(requestAny, responseHinter)
        else:
            chain.process(requestAny, responseFormat)

# --------------------------------------------------------------------

class EncoderPathHinter(EncoderPath):
    '''
    Provides hints in the URLs by showing all possible query parameters for a path.
    '''
    
    def __init__(self, wrapped, hintingHandler):
        '''
        @param wrapped: EncoderPath
            The encoder path to wrap for rendering paths.
        '''
        assert isinstance(wrapped, EncoderPath), 'Invalid encoder path to wrap %s' % wrapped
        assert isinstance(hintingHandler, HintingHandler), 'Invalid hinting handler %s' % hintingHandler
        self._wrapped = wrapped
        self._hintingHandler = hintingHandler
        
    def encode(self, path, parameters=None):
        '''
        @see: EncoderPath.encode
        '''
        assert isinstance(path, Path), 'Invalid path %s' % path
        if parameters is None:
            node = path.node
            assert isinstance(node, Node), \
            'The node has to be available in the path %s problems in previous processors' % path
            if node.get is not None:
                invoker = node.get
                assert isinstance(invoker, Invoker)
                # We only consider as parameters the not mandatory primitive inputs.
                inputs = [invoker.inputs[k] for k in range(invoker.mandatoryCount, len(invoker.inputs))]
                models = {}
                for inp in inputs:
                    for encoder in self._hintingHandler.encoders:
                        assert isinstance(encoder, EncoderParams)
                        encoder.encodeModels(inputs, inp, models)
                parameters = []
                for name, model in models.items():
                    isList = model[0]
                    value = model[2]
                    if value is None:
                        parameters.append((name, ''))
                    elif isList:
                        parameters.append((name, value[0]))
                    else:
                        parameters.append((name, value))
        return self._wrapped.encode(path, parameters)
