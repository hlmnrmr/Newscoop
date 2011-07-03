'''
Created on Jun 29, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoding handler.
'''

from ally.core.internationalization import msg as _
from ally.core.spec.charset import UTF_8
from ally.core.spec.codes import UNKNOWN_FORMAT
from ally.core.spec.presenting import EncoderFactory
from ally.core.spec.server import Processor, ProcessorsChain, ResponseFormat, \
    Response
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
    
    defaultEncoderFactory = EncoderFactory
    # The default encoder factory, to be used when there is no format provided.
    encoderFactories = list
    # A list of encoder factories that will be used by the encoding handler in order to provide encoders.
    charSet = UTF_8
    # The character set to use for writing the text.
    
    def __init__(self):
        if __debug__:
            for factory in self.encoderFactories:
                assert isinstance(factory, EncoderFactory), 'Invalid encoder factory %s' % factory
    
    def process(self, request, responseFormat, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if isinstance(responseFormat, ResponseFormat):
            assert isinstance(responseFormat, ResponseFormat)
            factory = self._findEncoderFactory(responseFormat.format)
            response = responseFormat.response
            assert isinstance(response, Response)
            if factory is None:
                response.setCode(UNKNOWN_FORMAT, _('Not supported format ($1)', responseFormat.format))
                log.debug('Unable to locate an encoder for format %s', responseFormat.format)
                return
            assert isinstance(factory, EncoderFactory)
            response.setCharSet(self.charSet)
            response.setContentType(factory.contentType)
            output = response.dispatch()
            def out(content):
                output.write(bytes(content, self.charSet.format))
            encoder = factory.createEncoder(responseFormat.encoderPath, out)
            log.debug('Created encoder with content type %s and character set %s', \
                      factory.contentType.content, self.charSet.format)
            chain.process(request, encoder)
                    
    def _findEncoderFactory(self, format):
        if format is None:
            return self.defaultEncoderFactory
        for factory in self.encoderFactories:
            assert isinstance(factory, EncoderFactory)
            if factory.isValidFormat(format):
                return factory
 
