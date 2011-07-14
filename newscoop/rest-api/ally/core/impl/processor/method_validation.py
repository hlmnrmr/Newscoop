'''
Created on Jul 14, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the requested method validation handler.
'''

from ally.core.internationalization import msg as _
from ally.core.spec.codes import METHOD_NOT_AVAILABLE
from ally.core.spec.resources import Path, Node
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain, \
    GET, INSERT, UPDATE, DELETE
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class MethodValidationHandler(Processor):
    '''
    Implementation for a processor that provides the validation of the requested resource node.
    '''
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
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
        elif req.method == INSERT: # Inserting
            invoker = node.insert
            if invoker is None:
                self._sendNotAvailable(node, rsp, _('Path not available for post'))
                return
        elif req.method == UPDATE: # Updating
            invoker = node.update
            if invoker is None:
                self._sendNotAvailable(node, rsp, _('Path not available for put'))
                return
        elif req.method == DELETE: # Deleting
            invoker = node.delete
            if invoker is None:
                self._sendNotAvailable(node, rsp, _('Path not available for delete'))
                return
        chain.process(req, rsp)

    def _processAllow(self, node, rsp):
        '''
        Set the allows for the response based on the provided node.
        '''
        assert isinstance(node, Node)
        assert isinstance(rsp, Response)
        if node.get is not None:
            rsp.addAllows(GET)
        if node.insert is not None:
            rsp.addAllows(INSERT)
        if node.update is not None:
            rsp.addAllows(UPDATE)
        if node.delete is not None:
            rsp.addAllows(DELETE)
            
    def _sendNotAvailable(self, node, rsp, message):
        self._processAllow(node, rsp)
        rsp.setCode(METHOD_NOT_AVAILABLE, message)
        log.warning('(%s) for node %s', message.default, node)
