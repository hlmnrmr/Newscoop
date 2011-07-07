'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invoking handler.
'''

from ally.core.internationalization import msg as _
from ally.core.spec.codes import NOT_AVAILABLE, INTERNAL_ERROR, \
    RESOURCE_NOT_FOUND, DELETED_SUCCESS, CANNOT_DELETE
from ally.core.spec.resources import Path, Node, Invoker
from ally.core.spec.server import Processor, ProcessorsChain, RequestResource, \
    RequestRender, Response, INSERT, UPDATE, DELETE, GET
import logging
import traceback
from ally.core.api.exception import InputException

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
            if requestResource.request.method == GET: # Retrieving
                invoker = node.get
                if invoker is None:
                    self._sendNotAvailable(node, response, _('Path not available for get'))
                    return
                assert isinstance(invoker, Invoker)
                argsDict = path.toArguments(invoker)
                argsDict.update(requestResource.arguments)
                try:
                    model = self._invoke(invoker, argsDict, response)
                    requestRender = RequestRender(requestResource, model, invoker.outputType)
                    chain.process(requestRender, responseAny)
                except: return
            elif requestResource.request.method == INSERT: # Inserting
                invoker = node.insert
                if invoker is None:
                    self._sendNotAvailable(node, response, _('Path not available for insert'))
                    return
                assert isinstance(invoker, Invoker)

            elif requestResource.request.method == UPDATE: # Updating
                invoker = node.update
                if invoker is None:
                    self._sendNotAvailable(node, response, _('Path not available for update'))
                    return
                assert isinstance(invoker, Invoker)
                
            elif requestResource.request.method == DELETE: # Deleting
                invoker = node.delete
                if invoker is None:
                    self._sendNotAvailable(node, response, _('Path not available for delete'))
                    return
                assert isinstance(invoker, Invoker)
                try:
                    value = self._invoke(invoker, path.toArguments(invoker), response)
                    if value == True:
                        response.setCode(DELETED_SUCCESS, _('Successfully deleted'))
                        log.debug('Successful deleted resource')
                        return
                    elif value == False:
                        response.setCode(CANNOT_DELETE, _('Cannot delete'))
                        log.debug('Cannot deleted resource')
                        return
                    else:
                        #If an entity is returned than we will render that.
                        requestRender = RequestRender(requestResource, value, invoker.outputType)
                        chain.process(requestRender, responseAny)
                except: return
            else:
                raise AssertionError('Cannot process request %s' % requestResource.request)
        else:
            chain.process(requestResource, responseAny)

    def _processAllow(self, node, response):
        '''
        Set the allows for the response based on the provided node.
        '''
        assert isinstance(node, Node)
        assert isinstance(response, Response)
        if node.get is not None:
            response.setAllows(GET)
        if node.insert is not None:
            response.setAllows(INSERT)
        if node.update is not None:
            response.setAllows(UPDATE)
        if node.delete is not None:
            response.setAllows(DELETE)
            
    def _sendNotAvailable(self, node, response, message):
        self._processAllow(node, response)
        response.setCode(NOT_AVAILABLE, message)
        log.warning('(%s) for node %s', message.default, node)
        
    def _invoke(self, invoker, argsDict, response):
        args = []
        for inp in invoker.inputs:
            try:
                args.append(argsDict[inp.name])
            except KeyError:
                args.append(None)
        try:
            value = invoker.invoke(*args)
            log.debug('Successful on calling invoker %s with values %s', invoker, args)
            return value
        except InputException as e:
            response.setCode(RESOURCE_NOT_FOUND, e.message)
            log.info('Input exception: %s', e.message.default)
            raise
        except:
            response.setCode(INTERNAL_ERROR, _('Upps, it seems I am in a pickle'))
            log.error('An exception occurred while trying to invoke %s with values %s', \
                      invoker, args)
            traceback.print_exc()
            raise
