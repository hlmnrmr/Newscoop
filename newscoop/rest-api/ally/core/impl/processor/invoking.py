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
from ally.core.spec.server import Processor, ProcessorsChain, Response, INSERT, UPDATE, DELETE, GET, \
    Request
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
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        path = req.resourcePath
        assert isinstance(path, Path)
        node = path.node
        assert isinstance(node, Node), \
        'The node has to be available in the path %s problems in previous processors' % path
        if req.method == GET: # Retrieving
            invoker = node.get
            if invoker is None:
                self._sendNotAvailable(node, rsp, _('Path not available for get'))
                return
            assert isinstance(invoker, Invoker)
            argsDict = path.toArguments(invoker)
            argsDict.update(req.arguments)
            try:
                req.objType = invoker.outputType
                req.obj = self._invoke(invoker, argsDict, rsp)
            except: return
        elif req.method == INSERT: # Inserting
            invoker = node.insert
            if invoker is None:
                self._sendNotAvailable(node, rsp, _('Path not available for insert'))
                return
            assert isinstance(invoker, Invoker)

        elif req.method == UPDATE: # Updating
            invoker = node.update
            if invoker is None:
                self._sendNotAvailable(node, rsp, _('Path not available for update'))
                return
            assert isinstance(invoker, Invoker)
            
        elif req.method == DELETE: # Deleting
            invoker = node.delete
            if invoker is None:
                self._sendNotAvailable(node, rsp, _('Path not available for delete'))
                return
            assert isinstance(invoker, Invoker)
            try:
                value = self._invoke(invoker, path.toArguments(invoker), rsp)
                if value == True:
                    rsp.setCode(DELETED_SUCCESS, _('Successfully deleted'))
                    log.debug('Successful deleted resource')
                    return
                elif value == False:
                    rsp.setCode(CANNOT_DELETE, _('Cannot delete'))
                    log.debug('Cannot deleted resource')
                    return
                else:
                    #If an entity is returned than we will render that.
                    req.objType = invoker.outputType
                    req.obj = value
            except: return
        else:
            raise AssertionError('Cannot process request method %s' % req.method)
        chain.process(req, rsp)

    def _processAllow(self, node, rsp):
        '''
        Set the allows for the response based on the provided node.
        '''
        assert isinstance(node, Node)
        assert isinstance(rsp, Response)
        if node.get is not None:
            rsp.setAllows(GET)
        if node.insert is not None:
            rsp.setAllows(INSERT)
        if node.update is not None:
            rsp.setAllows(UPDATE)
        if node.delete is not None:
            rsp.setAllows(DELETE)
            
    def _sendNotAvailable(self, node, rsp, message):
        self._processAllow(node, rsp)
        rsp.setCode(NOT_AVAILABLE, message)
        log.warning('(%s) for node %s', message.default, node)
        
    def _invoke(self, invoker, argsDict, rsp):
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
            rsp.setCode(RESOURCE_NOT_FOUND, e.message)
            log.info('Input exception: %s', e.message.default)
            raise
        except:
            rsp.setCode(INTERNAL_ERROR, _('Upps, it seems I am in a pickle'))
            log.error('An exception occurred while trying to invoke %s with values %s', \
                      invoker, args)
            traceback.print_exc()
            raise
