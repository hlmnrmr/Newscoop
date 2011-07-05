'''
Created on Jul 3, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters handler.
'''

from ally.core.api.exception import InputException
from ally.core.internationalization import msg as _
from ally.core.spec.codes import ILLEGAL_PARAM, UNKNOWN_PARAMS
from ally.core.spec.presenting import DecoderParams
from ally.core.spec.resources import Node, Invoker
from ally.core.spec.server import Processor, ProcessorsChain, RequestResource, \
    Response, GET
from ally.core.util import injected
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ParametersHandler(Processor):
    '''
    Implementation for a processor that provides the transformation of parameters into arguments, if this is required.
    '''
    
    decoders = list
    # The parameters decoders used for obtaining the arguments.
    
    def __init__(self):
        if __debug__:
            for decoder in self.decoders:
                assert isinstance(decoder, DecoderParams), 'Invalid parameters decoder %s' % decoder
    
    def process(self, requestResource, responseAny, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        response = self.findResponseIn(responseAny)
        if isinstance(requestResource, RequestResource) and requestResource.request.method == GET \
        and len(requestResource.parameters) > 0 and response is not None:
            assert isinstance(requestResource, RequestResource)
            assert isinstance(response, Response)
            node = requestResource.path.node
            assert isinstance(node, Node), \
            'The node has to be available in the path %s problems in previous processors' % requestResource.path
            if node.get is not None:
                invoker = node.get
                assert isinstance(invoker, Invoker)
                # We only consider as parameters the not mandatory primitive inputs.
                params = list(requestResource.parameters)
                inputs = [invoker.inputs[k] for k in range(invoker.mandatoryCount, len(invoker.inputs))]
                for inp in inputs:
                    for decoder in self.decoders:
                        assert isinstance(decoder, DecoderParams)
                        try:
                            decoder.decode(inputs, inp, params, requestResource.arguments)
                        except InputException as e:
                            assert isinstance(e, InputException)
                            response.setCode(ILLEGAL_PARAM, e.message)
                            log.warning('Problems converting parameters: %s', e.message.default)
                            return
                if len(params) > 0:
                    response.setCode(UNKNOWN_PARAMS, _('Unknown parameters: $1', \
                                                       ', '.join([param[0] for param in params])))
                    log.warning('Unsolved request parameters %s', params)
                    return
        chain.process(requestResource, responseAny)
