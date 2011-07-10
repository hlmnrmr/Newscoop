'''
Created on Jun 29, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoding handler.
'''

from ally.core.internationalization import msg as _
from ally.core.spec.codes import UNKNOWN_FORMAT
from ally.core.spec.presenting import EncoderFactory
from ally.core.spec.server import Processor, ProcessorsChain, Response
from ally.core.util import injected
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncodingHandler(Processor):
    '''
    Implementation for a processor that provides the encoder based on the requested format.    
    '''

    encoderFactories = dict
    # A dictionary having as a key the content type and as values the encoder factories that will be used by
    #the encoding handler in order to provide encoders.
    
    def __init__(self):
        assert isinstance(self.encoderFactories, dict), \
        'Invalid encoder factories dictionary %s' % self.encoderFactories
        if __debug__:
            for factory in self.encoderFactories.values():
                assert isinstance(factory, EncoderFactory), 'Invalid encoder factory %s' % factory
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        if not rsp.contentType in self.encoderFactories:
            rsp.setCode(UNKNOWN_FORMAT, _('Content type ($1) not supported', rsp.contentType))
            log.debug('No encoding factory available for content type %s', rsp.contentType)
            return
        factory = self.encoderFactories[rsp.contentType]
        assert isinstance(factory, EncoderFactory)
        rsp.encoder = factory.createEncoder(rsp, rsp.dispatch())
        log.debug('Created encoder with content type %s and character set %s', rsp.contentType, rsp.charSet)
        chain.process(req, rsp)
