'''
Created on Jun 29, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the encoding handler.
'''
from newscoop.core.spec.server import Processor, ProcessorsChain, ResponseFormat, \
    EncoderFactory, Response
from newscoop.core.spec.codes import UNKNOWN_FORMAT
from newscoop.core.spec.charset import UTF_8, CharSet
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class EncodingHandler(Processor):
    '''
    Implementation for a processor that provides the encoder based on the requested format.    
    '''
    
    def __init__(self, encoderFactories, charSet=UTF_8):
        '''
        @param encoderFactories: list
            A list of encoder factories that will be used by the encoding handler in order to provide encoders.
        @param charSet: CharSet
            The character set to use for writing the text.
        '''
        assert isinstance(encoderFactories, list), 'Invalid encoder factories list %s' % encoderFactories
        if __debug__:
            for factory in encoderFactories:
                assert isinstance(factory, EncoderFactory), 'Invalid encoder factory %s' % factory
        assert isinstance(charSet, CharSet), 'Invalid character set  %s' % charSet
        self._encoderFactories = encoderFactories
        self._charSet = charSet
    
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
            response.setCharSet(self._charSet)
            response.setContentType(factory.contentType)
            output = response.dispatch()
            def out(content):
                output.write(bytes(content, self._charSet.format))
            encoder = factory.createEncoder(responseFormat.encoderPath, out)
            log.debug('Created encoder with content type %s and character set %s', \
                      factory.contentType.name, self._charSet.format)
            chain.process(request, encoder)
                    
    def _findEncoderFactory(self, format):
        for factory in self._encoderFactories:
            assert isinstance(factory, EncoderFactory)
            if factory.isValidFormat(format):
                return factory
 
