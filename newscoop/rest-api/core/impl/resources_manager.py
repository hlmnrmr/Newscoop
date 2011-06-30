'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Module containing the implementation for the resources manager.
'''

from inspect import isclass
from newscoop.core.api.configure import serviceFor
from newscoop.core.api.operator import Service
from newscoop.core.api.type import List
from newscoop.core.impl.invoker import InvokerFunction, InvokerCall
from newscoop.core.impl.node import NodeRoot
from newscoop.core.spec.manager import ResourcesManager
from newscoop.core.spec.resources import Node, Path, Converter, Match, Assembler
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class ResourcesManagerImpl(ResourcesManager):
    '''
    @see: ResourcesManager container implementation.
    '''

    def __init__(self, assemblers):
        '''
        @param assemblers: list
            The list of assemblers to be used by this resources manager in order to register nodes.
        '''
        assert isinstance(assemblers, list), 'Invalid assemblers list %s' % assemblers
        if __debug__:
            for asm in assemblers:
                assert isinstance(asm, Assembler), 'Invalid assembler %s' % asm
        self._assemblers = assemblers
        self._root = NodeRoot(InvokerFunction(List(Path), self._rootPaths, [], 0))
    
    def register(self, service, implementation):
        '''
        @see: ResourcesManager.register
        '''
        if isclass(service):
            service = serviceFor(service)
        assert isinstance(service, Service), 'Invalid service %s' % service
        log.info('Assembling node structure for service %s', service)
        invokers = [InvokerCall(service, implementation, call) for call in service.calls.values()]
        for asm in self._assemblers:
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
        if len(paths) == 0:
            return Path(matches, node)
        return Path(matches)

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
