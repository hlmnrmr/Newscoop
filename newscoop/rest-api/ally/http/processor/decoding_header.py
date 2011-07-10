'''
Created on Jul 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the handler for decoding headers.
'''

from ally.core.internationalization import msg as _
from ally.http.spec import UNKNOWN_CONTENT_TYPE, UNKNOWN_CHARSET
from ally.core.spec.server import Processor, Response, ProcessorsChain
from ally.core.util import injected
from ally.http.spec import DecoderHeader, RequestHTTP
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingHeaderHandler(Processor):
    '''
    Implementation for a processor that provides the decoding of the request headers.
    '''
    
    decoders = list
    # The headers decoders used by the decoding.
    
    def __init__(self):
        assert isinstance(self.decoders, list), 'Invalid decoders list %s' % self.decoders
        if __debug__:
            for decoder in self.decoders:
                assert isinstance(decoder, DecoderHeader), 'Invalid decoder handler %s' % decoder
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid HTTP request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        for decoder in self.decoders:
            assert isinstance(decoder, DecoderHeader)
            decoder.decode(req)
        if len(req.accContentTypes) == 0:
            rsp.setCode(UNKNOWN_CONTENT_TYPE, _('Cannot provide any of the accepted content types'))
            log.debug('The server has not any of the accepted content types')
            return
        if len(req.accCharSets) == 0:
            rsp.setCode(UNKNOWN_CHARSET, _('Cannot provide any of the accepted character sets'))
            log.debug('The server has not any of the accepted character sets')
            return
        chain.process(req, rsp)
