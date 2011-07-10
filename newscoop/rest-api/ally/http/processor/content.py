'''
Created on Jul 10, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content handler.
'''

import logging
from ally.core.util import injected
from ally.core.spec.server import Processor, Response, ProcessorsChain, \
    INSERT, UPDATE, ContentOnFile
from ally.http.spec import ParserHeader, RequestHTTP, HeaderException, \
    UNKNOWN_CONTENT_LENGHT, UNKNOWN_CONTENT_TYPE

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ContentHandler(Processor):
    '''
    Implementation for a processor that provides the content of a request.
    '''
    
    parserContentType = ParserHeader
    # The parser used for getting the content type from the request headers.
    parserContentLength = ParserHeader
    # The parser used for getting the content length from the request headers.
    
    def __init__(self):
        assert isinstance(self.parserContentType, ParserHeader), 'Invalid parser %s' % self.parserContentType
        assert isinstance(self.parserContentLength, ParserHeader), 'Invalid parser %s' % self.parserContentLength
    
    def process(self, req, rsp, chain):
        assert isinstance(req, RequestHTTP), 'Invalid HTTP request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if req.method in (INSERT, UPDATE):
            try:
                contentType, charSet = self.parserContentType.parse(req.headers)
            except HeaderException as e:
                rsp.setCode(UNKNOWN_CONTENT_TYPE, e.message)
                log.warning('Invalid or no existent content type in the headers %s' % req.headers)
                return
            try:
                contentLength = self.parserContentLength.parse(req.headers)
            except HeaderException as e:
                rsp.setCode(UNKNOWN_CONTENT_LENGHT, e.message)
                log.warning('Invalid or no existent content length in the headers %s' % req.headers)
                return
            req.content = ContentOnFile(req.input, contentLength, contentType, charSet)
        chain.process(req, rsp)
