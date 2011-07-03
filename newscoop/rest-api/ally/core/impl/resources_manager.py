'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the implementation for the resources manager.
'''

from inspect import isclass
from ally.core.api.configure import serviceFor
from ally.core.api.operator import Service
from ally.core.api.type import List, TypeClass, Type, Input
from ally.core.impl.invoker import InvokerFunction, InvokerCall
from ally.core.impl.node import NodeRoot
from ally.core.spec.resources import Node, Path, Converter, Match, Assembler, \
    ResourcesManager, Invoker
import logging
from ally.core.util import injected

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
        if __debug__:
            for asm in self.assemblers:
                assert isinstance(asm, Assembler), 'Invalid assembler %s' % asm
        self._root = NodeRoot(InvokerFunction(List(TypeClass(Path, False)), self._rootPaths, [], 0))
        for service in self.services:
            self.register(serviceFor(service), service)
    
    def register(self, service, implementation):
        #TODO: there is still stiff to do here, for instance the implementation is not mandatory
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
            log.warning('The call %s could not be resolved in the node structure', invoker.call)

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
                if match is not None and match is not False:
                    if isinstance(match, list):
                        matches.extend(match)
                    elif isinstance(match, Match):
                        matches.append(match)
                    elif match is not True:
                        raise AssertionError('Invalid return value %s for %s' % (match, child))
                    node = child
                    found = True
                    break
        if len(paths) == 0:
            return Path(matches, node)
        return Path(matches)
    
    def findAllPaths(self, outputType, *inputTypes):
        '''
        @see: ResourcesManager.findAllPaths
        '''
        assert outputType is None or isinstance(outputType, Type), 'Invalid output type in list %s' % outputType
        if __debug__:
            for typ in inputTypes:
                assert isinstance(typ, Type), 'Invalid input type %s' % typ
        nodes = []
        self._searchGetNodes(self._root, outputType, inputTypes, nodes, False)
        paths = []
        for node in nodes:
            paths.append(self._getPathForNode(node))
        return paths
    
    def findShortPath(self, outputType, *inputTypes):
        '''
        @see: ResourcesManager.findPathForInputType
        '''
        assert outputType is None or isinstance(outputType, Type), 'Invalid output type in list %s' % outputType
        if __debug__:
            for typ in inputTypes:
                assert isinstance(typ, Type), 'Invalid input type %s' % typ
        nodes = []
        self._searchGetNodes(self._root, outputType, inputTypes, nodes, True)
        if len(nodes) > 0:
            return self._getPathForNode(nodes[0])
        return None

    def _rootPaths(self):
        '''
        FOR INTERNAL USE ONLY.
        Provides the root resources paths.
        
        @return: list
            A list of Paths from the root node.
        '''
        paths = []
        for child in self._root.childrens():
            assert isinstance(child, Node)
            if child.get is not None:
                match = child.newMatch()
                if match is not None:
                    paths.append(Path([match], child))
        return paths

    def _searchGetNodes(self, node, outputType, inputTypes, nodes, onlyOne):
        '''
        FOR INTERNAL USE ONLY.
        Finds the node that has the specified input types list.
        '''
        assert isinstance(node, Node)
        if node.get is not None:
            get = node.get
            assert isinstance(get, Invoker)
            equals = True
            if outputType is not None and get.outputType != outputType:
                equals = False
            if equals and get.mandatoryCount == len(inputTypes):
                for inp, typ in zip(get.inputs, inputTypes):
                    assert isinstance(inp, Input)
                    if inp.type != typ:
                        equals = False
                        break
            if equals:
                nodes.append(node)
                if onlyOne: return True
        for child in node.childrens():
            if self._searchGetNodes(child, outputType, inputTypes, nodes, onlyOne):
                return True

    def _getPathForNode(self, node):
        '''
        FOR INTERNAL USE ONLY.
        Builds a Path for the node.
        '''
        n = node
        assert isinstance(n, Node)
        matches = []
        while n is not None:
            m = n.newMatch()
            if m is not None:
                if isinstance(m, list):
                    matches[0:] = m
                else:
                    matches.insert(0, m)
            n = n.parent
        return Path(matches, node)
