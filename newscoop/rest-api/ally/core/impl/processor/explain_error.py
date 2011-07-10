'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Provides support for explaining the errors in the content of the request.
'''

from ally.core.spec.content_type import XML
from ally.core.spec.server import Response, Processor, ProcessorsChain
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

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        
        chain.process(req, rsp)
        if not rsp.code.isSuccess:
            rsp.contentType = XML
            out = rsp.dispatch()
            log.debug('Error code received %s formating error content response', rsp.code.code)
            out.write(
            (
'''<?xml version="1.0"?>
<error>
    <code>%(code)d</code>
    <message>%(message)s</message>
</error>''' % 
            {'code': rsp.code.code, 'message': rsp.message.default})
            .encode('UTF-8', 'replace'))
