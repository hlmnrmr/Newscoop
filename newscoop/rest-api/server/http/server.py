'''
Created on Jun 17, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the web server.
'''

import logging

logging.basicConfig(level=logging.DEBUG)

# --------------------------------------------------------------------

from http.server import HTTPServer, BaseHTTPRequestHandler
from newscoop.api import publication, resource, theme
from newscoop.core import resources
from newscoop.core.resources import Converter, Path
from newscoop.server.encoder import Encoder
from newscoop.server.processing import Chain, EncoderProvider, NodeFinder, \
    Context, OutputEncoding, GET, ActionCheck, GETEncoder, LinkResources
from newscoop.impl import publication as impl

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

SERVER_LOCATION = 'http://localhost/'

PATH_CONVERTER = Converter()

RESOLVE = Chain([ NodeFinder(PATH_CONVERTER), ActionCheck(), OutputEncoding(), EncoderProvider()])

ENCODE = Chain([GETEncoder([LinkResources(PATH_CONVERTER)])])

# --------------------------------------------------------------------

class PathHTTP(Path):
    '''
    HTTP type path implementation.
    '''
    
    def __init__(self, httpPath):
        '''
        @param httpPath: string
            The full HTTP path.
        '''
        paths = httpPath.split('/')
        i = paths[-1].rfind('.')
        if i < 0:
            extension = None
        else:
            extension = paths[-1][i + 1:].lower()
            paths[-1] = paths[-1][0:i]
        paths = [path for path in paths if len(path) != 0]
        super().__init__(paths, '/', '.', SERVER_LOCATION, extension)

# --------------------------------------------------------------------

class Server(BaseHTTPRequestHandler):
    '''
    The server class that handles the HTTP requests.
    '''

    def do_GET(self):
        context = Context(PathHTTP(self.path), self.rfile.read, self.wfile.write, GET)
        RESOLVE.process(context)
        if context.aborted:
            self.send_error(context.status, None if context.message is None else context.message.default)
            return
        self.send_response(context.status, None if context.message is None else context.message.default)
        assert isinstance(context.encoder, Encoder)
        self.send_header('Content-type', 'text/' + context.encoder.format)
        self.end_headers()
        ENCODE.process(context)

    def do_POST(self):
        pass

# --------------------------------------------------------------------

def main():
    resources.register(publication.IPublicationService, impl.PublicationServiceTest())
    resources.register(resource.IResourceService)
    resources.register(theme.IThemeService)

    try:
        server = HTTPServer(('', 80), Server)
        print('started httpserver...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()

if __name__ == '__main__':
    main()
