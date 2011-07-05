'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invoking handler.
'''

from ally.core.internationalization import msg as _
from ally.core.spec.codes import NOT_AVAILABLE, INTERNAL_ERROR
from ally.core.spec.resources import Path, Node, Invoker
from ally.core.spec.server import Processor, ProcessorsChain, RequestResource, \
    RequestRender, Response, INSERT, UPDATE, DELETE, GET
import logging
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
            assert isinstance(response, Response)
            path = requestResource.path
            assert isinstance(path, Path)
            node = path.node
            assert isinstance(node, Node), \
            'The node has to be available in the path %s problems in previous processors' % path
            if requestResource.request.method == GET:
                invoker = node.get
                if invoker is None:
                    if node.insert is not None:
                        response.setAllows(INSERT)
                    if node.update is not None:
                        response.setAllows(UPDATE)
                    if node.delete is not None:
                        response.setAllows(DELETE)
                    response.setCode(NOT_AVAILABLE, _('Path not available for get'))
                    log.warning('Cannot find a get method for node %s', node)
                    return
                assert isinstance(invoker, Invoker)
                argsDict = path.toArguments()
                argsDict.update(requestResource.arguments)
                args = []
                for inp in invoker.inputs:
                    try:
                        args.append(argsDict[inp.name])
                    except KeyError:
                        args.append(None)
                try:
                    model = invoker.invoke(*args)
                    requestRender = RequestRender(requestResource, model, invoker.outputType)
                    log.debug('Successful obtained model from invoker %s with values %s', invoker, args)
                    chain.process(requestRender, responseAny)
                except:
                    response.setCode(INTERNAL_ERROR, _('Upps, it seems I am in a pickle'))
                    log.error('An exception occurred while trying to invoke %s with values %s', \
                              invoker, args)
                    traceback.print_exc()
                    return
            else:
                raise AssertionError('Cannot process request %s' % requestResource.request)
        else:
            chain.process(requestResource, responseAny)
