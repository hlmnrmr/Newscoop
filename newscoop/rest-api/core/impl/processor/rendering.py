'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the rendering for a render request.
'''
import logging
from newscoop.core.spec.server import Processor, ProcessorsChain, \
    RequestResource, RequestGet, RequestRender, Encoder
from newscoop.core.spec.resources import Path, Node, Invoker
from newscoop.core.spec.codes import NOT_AVAILABLE, INTERNAL_ERROR
import traceback

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class RenderingHandler(Processor):
    '''
    Implementation for a processor that provides the rendering for a render request.
    '''
    
    def process(self, requestRender, encoder, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if isinstance(requestRender, RequestRender) and isinstance(encoder, Encoder):
            pass
