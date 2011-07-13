'''
Created on Jul 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the web server.
'''

from ally.core.spec.codes import Code
from ally.core.spec.server import Response, Processors, ProcessorsChain, GET, \
    INSERT, UPDATE, DELETE
from http.server import HTTPServer, BaseHTTPRequestHandler
from ally.http.spec import EncoderHeader, RequestHTTP
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class HTTPResponse(Response):
    '''
    Provides the dispatch functionality for an HTTP response.
    '''
    
    def __init__(self, requestHandler):
        ''''
        @see: Response.__init__
        
        @param requestHandler: RequestHandler
            The request handler used for rendering response data.
        '''
        super().__init__()
        assert isinstance(requestHandler, RequestHandler), 'Invalid request handler %s' % requestHandler
        self.requestHandler = requestHandler
        self.isDispatched = False

    def dispatch(self):
        '''
        @see: Response.dispatch
        '''
        assert self.code is not None, 'No code provided for dispatching.'
        assert not self.isDispatched, 'Already dispatched'
        rq = self.requestHandler
        assert isinstance(rq, RequestHandler)
        headers = {}
        for headerEncoder in rq.encodersHeader:
            assert isinstance(headerEncoder, EncoderHeader)
            headerEncoder.encode(headers, self)
        for name, value in headers.items():
            rq.send_header(name, value)
        msg = None
        if self.message is not None:
            msg = self.message.default
        code = self.code
        assert isinstance(code, Code)
        rq.send_response(code.code, msg)
        rq.end_headers()
        self.isDispatched = True
        return rq.wfile
        
# --------------------------------------------------------------------

class RequestHandler(BaseHTTPRequestHandler):
    '''
    The server class that handles the HTTP requests.
    '''
    
    processors = Processors
    # The processors used by the request handler
    encodersHeader = list
    # The header encoders

    def do_GET(self):
        self._process(GET)

    
    def do_POST(self):
        self._process(INSERT)
        
    def do_PUT(self):
        self._process(UPDATE)
        
    def do_DELETE(self):
        self._process(DELETE)
            
    def _process(self, method):
        chain = self.processors.newChain()
        assert isinstance(chain, ProcessorsChain)
        req = RequestHTTP()
        req.method = method
        req.path = self.path
        req.headers = dict(self.headers)
        req.input = self.rfile
        rsp = HTTPResponse(self)
        chain.process(req, rsp)
        if not rsp.isDispatched:
            rsp.dispatch()
        log.debug('Finalized request: %s and response: %s' % (req.__dict__, rsp.__dict__))
           
# --------------------------------------------------------------------

port = 80
# To be injected before setup, provides the port of the server.

def run():
    try:
        server = HTTPServer(('', port), RequestHandler)
        print('Started HTTP REST API server...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()
