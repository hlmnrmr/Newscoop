'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Provides support for explaining the errors in the content of the request.
'''

from _abcoll import Callable
from ally.core.spec.content_type import XML
from ally.core.spec.server import Request, Response, Processor, ProcessorsChain
from ally.core.util import injected
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ExplainErrorHandler(Processor):
    '''
    Implementation for a processor that provides the URI conversion to a resource path.
    '''

    def process(self, request, response, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if isinstance(request, Request) and isinstance(response, Response):
            assert isinstance(response, Response)
            response.dispatch = ExplainErrorDispatch(response, response.dispatch)
        chain.process(request, response)
            
# --------------------------------------------------------------------

class ExplainErrorDispatch:
    '''
    Callable class that handles the presentation of an error message in content.
    '''
    
    def __init__(self, response, dispatch):
        '''
        @param response: Response
            The response object that will be monitored for errors and provide error content.
        @param dispatch: Callable
            The real dispatch method of the response that is wrapped by this error.
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(dispatch, Callable), 'Invalid dispatch callable %s' % dispatch
        self.response = response 
        self.dispatch = dispatch
        
    def __call__(self):
        resp = self.response
        assert isinstance(resp, Response)
        resp.setContentType(resp.contentType or XML)
        # ending headers here!
        out = self.dispatch()
        if not self.response.code.isSuccess :
            log.debug('Error code received %s formating error content response', self.response.code.code)
            rqh = self.response.requestHandler
            rqh.wfile.write(
                ('<?xml version="1.0"?>\
                <error>\
                <code>%(code)d</code>\
                <message>%(message)s</message>\
                </error>' % 
                {'code': self.response.code.code, 'message': self.response.message.default})
                .encode('UTF-8', 'replace'))
        return out
