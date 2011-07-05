'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the URI request path handler.
'''
from _pyio import StringIO
from ally.core.impl.node import NodeModel
from ally.core.internationalization import msg as _
from ally.core.spec.codes import RESOURCE_NOT_FOUND, RESOURCE_FOUND, Code
from ally.core.spec.resources import Converter, Path, ResourcesManager
from ally.core.spec.server import Request, Response, Processor, ProcessorsChain, \
    RequestResource, ResponseFormat, EncoderPath
from ally.core.util import injected
import logging
from ally.core.spec import codes
from ally.core.spec.charset import UTF_8
from ally.core.spec.content_type import XML

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ExplainErrorHandler(Processor):
    '''
    Implementation for a processor that provides the URI conversion to a resource path.
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager that will provide the path to the resource node.
    converter = Converter
    # The converter to be used in handling the path.
    domain = str
    # The path domain something like "http://localhost/".
    separatorPath = '/'
    # The path separator.
    separatorExtension = '.'
    # The extension separator.
    separatorQuery = '?'
    # The query parameters separator.
    separatorParam = '&'
    # The separator for parameters inside a query.
    separatorValue = '='
    # The separator used in parameter to separate name from value.
    separatorList = ','
    # The separator used in defining a list of values.


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
    
    '''
    def __init__(self, response, dispatch):
        assert isinstance(response, Response), 'Invalid response %s' % response
        self.response = response 
        self.dispatch = dispatch
        
    def __call__(self):
        resp = self.response
        assert isinstance(resp, Response)
        resp.setContentType(resp.contentType)
        # ending headers here!
        out = self.dispatch()
        if not self.response.code.isSuccess :
            rqh = self.response.requestHandler
            rqh.wfile.write(
                ('<?xml version="1.0"?>\
                <error>\
                <code>%(code)d</code>\
                <message>%(message)s</message>\
                </error>' %
                {'code': self.response.code.code, 'message': self.response.message.msg})
                .encode('UTF-8', 'replace'))
            
        return out
