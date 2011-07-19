'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invoking handler.
'''

from ally.core.api.exception import InputException
from ally.core.api.type import isBool, isPropertyTypeId
from ally.core.internationalization import msg as _
from ally.core.spec.codes import INTERNAL_ERROR, RESOURCE_NOT_FOUND, \
    DELETED_SUCCESS, CANNOT_DELETE, UPDATE_SUCCESS, CANNOT_UPDATE, \
    INSERT_SUCCESS, CANNOT_INSERT
from ally.core.spec.resources import Path, Node, Invoker, ResourcesManager
from ally.core.spec.server import Processor, ProcessorsChain, Response, INSERT, \
    UPDATE, DELETE, GET, Request
import logging
import traceback
from ally.core.util import injected

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class InvokingHandler(Processor):
    '''
    Implementation for a processor that provides the invoking for the node in order to get the resources 
    for rendering.    
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the resource paths for the id's presented.
    
    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
    
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
        assert isinstance(node, Node)
        if req.method == GET: # Retrieving
            invoker = node.get
            assert isinstance(invoker, Invoker)
            argsDict = path.toArguments(invoker)
            argsDict.update(req.arguments)
            try:
                req.objType = invoker.outputType
                req.obj = self._invoke(invoker, argsDict, rsp)
            except: return
        elif req.method == INSERT: # Inserting
            invoker = node.insert
            assert isinstance(invoker, Invoker)
            argsDict = path.toArguments(invoker)
            argsDict.update(req.arguments)
            try:
                value = self._invoke(invoker, argsDict, rsp)
            except: return
            if isPropertyTypeId(invoker.outputType):
                if value is not None:
                    path = self.resourcesManager.findGetModel(req.resourcePath, invoker.outputType.model)
                    if path is not None:
                        path.update(value, invoker.outputType)
                        rsp.contentLocation = path
                    else:
                        req.objType = invoker.outputType
                        req.obj = value
                else:
                    rsp.setCode(CANNOT_INSERT, _('Cannot insert'))
                    log.debug('Cannot updated resource')
                    return
            else:
                req.objType = invoker.outputType
                req.obj = value
            rsp.setCode(INSERT_SUCCESS, _('Successfully created'))
        elif req.method == UPDATE: # Updating
            invoker = node.update
            assert isinstance(invoker, Invoker)
            argsDict = path.toArguments(invoker)
            argsDict.update(req.arguments)
            try:
                value = self._invoke(invoker, argsDict, rsp)
            except: return
            if isBool(invoker.outputType):
                if value == True:
                    rsp.setCode(UPDATE_SUCCESS, _('Successfully updated'))
                    log.debug('Successful updated resource')
                else:
                    rsp.setCode(CANNOT_UPDATE, _('Cannot updated'))
                    log.debug('Cannot updated resource')
                return
            else:
                #If an entity is returned than we will render that.
                req.objType = invoker.outputType
                req.obj = value
        elif req.method == DELETE: # Deleting
            invoker = node.delete
            assert isinstance(invoker, Invoker)
            try:
                value = self._invoke(invoker, path.toArguments(invoker), rsp)
            except: return
            if isBool(invoker.outputType):
                if value == True:
                    rsp.setCode(DELETED_SUCCESS, _('Successfully deleted'))
                    log.debug('Successful deleted resource')
                else:
                    rsp.setCode(CANNOT_DELETE, _('Cannot delete'))
                    log.debug('Cannot deleted resource')
                return
            else:
                #If an entity is returned than we will render that.
                req.objType = invoker.outputType
                req.obj = value
        else:
            raise AssertionError('Cannot process request method %s' % req.method)
        chain.process(req, rsp)
        
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
