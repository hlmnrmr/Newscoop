'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the invoking handler.
'''

import logging
from newscoop.core.spec.server import Processor, ProcessorsChain, \
    RequestResource, RequestGet, RequestRender
from newscoop.core.spec.resources import Path, Node, Invoker
from newscoop.core.spec.codes import NOT_AVAILABLE, INTERNAL_ERROR
import traceback

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class InvokingHandler(Processor):
    '''
    Implementation for a processor that provides the invoking for the node in order to get the resources 
    for rendering.    
    '''
    
    def process(self, requestResource, responseAny, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        response = self.findResponseIn(responseAny)
        if isinstance(requestResource, RequestResource) and response is not None:
            assert isinstance(requestResource, RequestResource)
            path = requestResource.path
            assert isinstance(path, Path)
            node = path.node
            assert isinstance(node, Node), \
            'The node has to be available in the path %s there is something wrong with the previous processors' % path
            if isinstance(requestResource.request, RequestGet):
                invoker = node.get
                if invoker is None:
                    response.setCode(NOT_AVAILABLE, _('Path not available for getting'))
                    log.debug('Cannot find a get method for node %s', node)
                    return
                assert isinstance(invoker, Invoker)
                try:
                    model = invoker.invoke(*path.values())
                    requestRender = RequestRender(requestResource, model, invoker.outputType)
                    chain.process(requestRender, responseAny)
                except:
                    response.setCode(INTERNAL_ERROR, _('Upps, it seems I am in a pickle'))
                    log.error('An exception occurred while trying to invoke %s with values %s', \
                              invoker, path.values())
                    traceback.print_exc()
                return
            else:
                raise AssertionError('Cannot process request %s' % requestResource.request)
        chain.process(requestResource, responseAny)
