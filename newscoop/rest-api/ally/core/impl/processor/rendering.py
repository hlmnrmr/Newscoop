'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the rendering for a render request.
'''

from ally.core.spec.presenting import Renders, Encoder
from ally.core.spec.server import Processor, ProcessorsChain, RequestRender
import logging
from ally.core.util import injected

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class RenderingHandler(Processor):
    '''
    Implementation for a processor that provides the rendering for a render request.
    '''
    
    renders = Renders
    # The renders to be used by this rendering handler.
    
    def process(self, requestRender, encoder, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if isinstance(requestRender, RequestRender) and isinstance(encoder, Encoder):
            assert isinstance(requestRender, RequestRender) 
            log.debug('Rendering object of type %s to encoder %s', requestRender.objType, encoder)
            self.renders.render(requestRender.obj, requestRender.objType, encoder)
        chain.process(requestRender, encoder)
