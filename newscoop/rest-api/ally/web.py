'''
Created on Jul 1, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the web server.
'''

from ally.core.spec.codes import Code
from ally.core.spec.server import Response, Processors, ProcessorsChain, GET, \
    INSERT, UPDATE, DELETE, Request
from http.server import HTTPServer, BaseHTTPRequestHandler

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
        if self.contentType is not None:
            cntTyp = self.contentType.content
            if self.charSet is not None:
                cntTyp = cntTyp + ';' + self.charSet.format
            rq.send_header('Content-type', cntTyp)
        if self.allows != 0:
            allow = []
            if self.allows & GET != 0: allow.append('GET')
            if self.allows & DELETE != 0: allow.append('DELETE')
            if self.allows & INSERT != 0: allow.append('POST')
            if self.allows & UPDATE != 0: allow.append('PUT')
            rq.send_header('Allow', ', '.join(self.allows))
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

    def do_GET(self):
        chain = self.processors.newChain()
        assert isinstance(chain, ProcessorsChain)
        response = HTTPResponse(self)
        chain.process(Request(GET, self.path), response)
        if not response.isDispatched:
            response.dispatch()
        
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

    
