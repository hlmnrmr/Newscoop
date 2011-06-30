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

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class RenderingHandler(Processor):
    '''
    Implementation for a processor that provides the rendering for a render request.
    '''
    
    def __init__(self, renders):
        '''
        Constructs the rendering processor.
        
        @param renders: Renders
            The renders to be used by this rendering handler.
        '''
        assert isinstance(renders, Renders), 'Invalid renders %s' % renders
        self.renders = renders
    
    def process(self, requestRender, encoder, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if isinstance(requestRender, RequestRender) and isinstance(encoder, Encoder):
            assert isinstance(requestRender, RequestRender) 
            self.renders.render(requestRender.obj, requestRender.objType, encoder)
        chain.process(requestRender, encoder)
