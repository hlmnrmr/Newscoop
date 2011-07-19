'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the implementation for the resources manager.
'''

from ally.core.api.configure import serviceFor
from ally.core.api.operator import Service, Model
from ally.core.api.type import List, TypeClass
from ally.core.impl.invoker import InvokerFunction, InvokerCall
from ally.core.impl.node import NodeRoot, NodePath, NodeModel, NodeId
from ally.core.spec.resources import Node, Path, Converter, Match, Assembler, \
    ResourcesManager, PathExtended
from ally.core.util import injected
from inspect import isclass
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ResourcesManagerImpl(ResourcesManager):
    '''
    @see: ResourcesManager container implementation.
    '''
    
    assemblers = list
    # The list of assemblers to be used by this resources manager in order to register nodes.
    services = list
    # The list of services to be registered, the list contains the service instance.

    def __init__(self):
        assert isinstance(self.assemblers, list), 'Invalid assemblers list %s' % self.assemblers
        assert isinstance(self.services, list), 'Invalid services list %s' % self.services
        if __debug__:
            for asm in self.assemblers:
                assert isinstance(asm, Assembler), 'Invalid assembler %s' % asm
        def resources():
            return self.findGetAllAccessible(self._rootPath)
        self._root = NodeRoot(InvokerFunction(List(TypeClass(Path, False)), resources, [], 0))
        self._rootPath = Path([], self._root)
        for service in self.services:
            self.register(serviceFor(service), service)
    
    def register(self, service, implementation):
        #TODO: there is still stuff to do here, for instance the implementation is not mandatory
        # at this point.
        '''
        @see: ResourcesManager.register
        '''
        if isclass(service):
            service = serviceFor(service)
        assert isinstance(service, Service), 'Invalid service %s' % service
        log.info('Assembling node structure for service %s', service)
        invokers = [InvokerCall(service, implementation, call) for call in service.calls.values()]
        for asm in self.assemblers:
            asm.assemble(self._root, invokers)
        for invoker in invokers:
            assert isinstance(invoker, InvokerCall)
            log.warning('The service %s call %s could not be resolved in the node structure', \
                        invoker.service, invoker.call)

    def findResourcePath(self, converter, paths):
        '''
        @see: ResourcesManager.findResourcePath
        '''
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter
        assert isinstance(paths, list), 'Invalid paths %s' % paths
        if len(paths) == 0:
            return Path([], self._root)
        node = self._root
        matches = []
        found = True
        while found and len(paths) > 0:
            found = False
            for child in node.childrens():
                assert isinstance(child, Node)
                match = child.tryMatch(converter, paths)
                if self._addMatch(matches, match):
                    node = child
                    found = True
                    break
        if len(paths) == 0:
            return Path(matches, node)
        return Path(matches)
    
    def findGetModel(self, fromPath, model):
        '''
        @see: ResourcesManager.findGetModel
        '''
        assert isinstance(fromPath, Path), 'Invalid from path %s' % fromPath
        assert isinstance(fromPath.node, Node), 'Invalid from path Node %s' % fromPath.node
        assert isinstance(model, Model), 'Invalid model %s' % model
        index = len(fromPath.matches) - 1
        while index >= 0:
            node = fromPath.matches[index].node
            assert isinstance(node, Node)
            if isinstance(node, NodeModel) and node.model == model:
                for nodeId in node.childrens():
                    if isinstance(nodeId, NodeId) and nodeId.get is not None:
                        matches = []
                        self._addMatch(matches, nodeId.newMatch())
                        return PathExtended(fromPath, matches, nodeId, index + 1)
            for child in node.childrens():
                assert isinstance(child, Node)
                if isinstance(child, NodeModel) and child.model == model:
                    for nodeId in child.childrens():
                        if isinstance(nodeId, NodeId) and nodeId.get is not None:
                            matches = []
                            self._addMatch(matches, child.newMatch())
                            self._addMatch(matches, nodeId.newMatch())
                            return PathExtended(fromPath, matches, nodeId, index + 1)
            index -= 1
        return None
        
    def findGetAllAccessible(self, fromPath):
        '''
        @see: ResourcesManager.findGetAllAccessible
        '''
        assert isinstance(fromPath, Path), 'Invalid from path %s' % fromPath
        assert isinstance(fromPath.node, Node), 'Invalid from path Node %s' % fromPath.node
        paths = []
        for child in fromPath.node.childrens():
            assert isinstance(child, Node)
            if child.get is not None and isinstance(child, NodePath):
                matches = []
                self._addMatch(matches, child.newMatch())
                if all([match.isValid() for match in matches]):
                    extended = PathExtended(fromPath, matches, child)
                    paths.append(extended)
                    paths.extend(self.findGetAllAccessible(extended))
        return paths

    def _addMatch(self, matches, match):
        '''
        FOR INTERNAL USE ONLY.
        Adds the match to the matches list, returns True if the match(es) have been added successfully, False if no
        match was added.
        '''
        if match is not None and match is not False:
            if isinstance(match, list):
                matches.extend(match)
            elif isinstance(match, Match):
                matches.append(match)
            elif match is not True:
                raise AssertionError('Invalid match value %s') % match
            return True
        return False
