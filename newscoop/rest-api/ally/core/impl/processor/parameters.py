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
from ally.core.spec.resources import Invoker
from ally.core.spec.server import Processor, ProcessorsChain, Response, Request, \
    GET
from ally.core.util import injected
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ParametersHandler(Processor):
    '''
    Implementation for a processor that provides the transformation of parameters into arguments, the parameters will
    be parsed only for the GET method, for other methods will throw exception.
    '''
    
    decoders = list
    # The parameters decoders used for obtaining the arguments.
    
    def __init__(self):
        assert isinstance(self.decoders, list), 'Invalid decoders list %s' % self.decoders
        if __debug__:
            for decoder in self.decoders:
                assert isinstance(decoder, DecoderParams), 'Invalid parameters decoder %s' % decoder
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        req.arguments = {}
        if len(req.params) > 0:
            if req.method == GET:
                invoker = req.resourcePath.node.get
                assert isinstance(invoker, Invoker)
                # We only consider as parameters the not mandatory primitive inputs.
                params = list(req.params)
                inputs = [invoker.inputs[k] for k in range(invoker.mandatoryCount, len(invoker.inputs))]
                for inp in inputs:
                    for decoder in self.decoders:
                        assert isinstance(decoder, DecoderParams)
                        try:
                            decoder.decode(inputs, inp, params, req.arguments)
                        except InputException as e:
                            assert isinstance(e, InputException)
                            rsp.setCode(ILLEGAL_PARAM, e.message)
                            log.warning('Problems converting parameters: %s', e.message.default)
                            return
                if len(params) > 0:
                    rsp.setCode(UNKNOWN_PARAMS, _('Unknown parameters: $1', ', '.join([param[0] for param in params])))
                    log.warning('Unsolved request parameters %s', params)
                    return
            else:
                rsp.setCode(UNKNOWN_PARAMS, _('Illegal parameters: $1', \
                                              ', '.join([param[0] for param in req.params])))
                log.warning('Illegal method %s for parameters', req.method)
                return
        chain.process(req, rsp)
