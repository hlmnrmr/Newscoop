'''
Created on Jul 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the decoding handler.
'''

from ally.core.internationalization import msg as _
from ally.core.spec.codes import UNKNOWN_DECODING
from ally.core.spec.server import Processor, ProcessorsChain, Request, INSERT, \
    UPDATE, Response, Processors
from ally.core.util import injected
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingHandler(Processor):
    '''
    Implementation for a processor that provides the decoding of the request input file based on the
    requested format.    
    '''
    
    decodings = Processors
    # The decodings processors, if a processor is successful in the decoding process it has to stop the chain
    # execution.
    
    def __init__(self):
        assert isinstance(self.decodings, Processors), 'Invalid decodings processors %s' % self.decodings
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if req.method in (INSERT, UPDATE):
            decodingChain = self.decodings.newChain()
            assert isinstance(decodingChain, ProcessorsChain)
            decodingChain.process(req, rsp)
            if decodingChain.isConsumed():
                rsp.setCode(UNKNOWN_DECODING, _('Content type ($1) not supported for decoding', rsp.contentType))
                log.debug('No decoding processor available for content type %s', rsp.contentType)
                return
            if rsp.code is not None and not rsp.code.isSuccess:
                # A failure occurred in decoding, stopping chain execution
                return
        chain.process(req, rsp)
