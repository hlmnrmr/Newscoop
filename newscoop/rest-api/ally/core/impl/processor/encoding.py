'''
Created on Jul 12, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoding processing node.
'''

from ally.core.internationalization import msg as _
from ally.core.spec.codes import UNKNOWN_ENCODING
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain, \
    Processors
from ally.core.util import injected
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------
    
@injected
class EncodingProcessorsHandler(Processor):
    '''
    Provides the support for executing the encoding processors, if a processor is successful in the encoding process
    it has to stop the chain execution.
    '''
    
    encodings = Processors
    # The encoding processors, if a processor is successful in the encoding process it has to stop the chain execution.
    
    def __init__(self):
        assert isinstance(self.encodings, Processors), 'Invalid encodings processors %s' % self.encodings
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        encodingChain = self.encodings.newChain()
        assert isinstance(encodingChain, ProcessorsChain)
        encodingChain.process(req, rsp)
        if encodingChain.isConsumed():
            rsp.setCode(UNKNOWN_ENCODING, _('Content type ($1) not supported', rsp.contentType))
            log.debug('No encoding processor available for content type %s', rsp.contentType)
            return
        chain.process(req, rsp)
