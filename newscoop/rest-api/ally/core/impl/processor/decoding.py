'''
Created on Jul 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the decoding handler.
'''

from ally.core.spec.server import Processor, ProcessorsChain, Request, INSERT, \
    UPDATE, Response
from ally.core.util import injected
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingHandler(Processor):
    '''
    Implementation for a processor that provides the decoding of the request input file based on the
    requested format.    
    '''
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if req.method in (INSERT, UPDATE):
            #TODO: remove
            print(req.content.read())
                 
        chain.process(req, rsp)
