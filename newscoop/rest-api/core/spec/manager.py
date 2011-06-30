'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Module containing specifications for the managers.
'''

from newscoop.core.util import guard
import abc

# --------------------------------------------------------------------

@guard
class ResourcesManager(metaclass=abc.ABCMeta):
    '''
    Provides the specifications for the resources manager. This manager will contain the resources tree and provide
    abilities to update the tree and also to find resources.
    @attention: This class might require thread safety latter on the line when we are doing the model property update.
    '''
    
    @abc.abstractmethod
    def register(self, service, implementation):
        '''
        Register the provided service class into the resource node tree.
    
        @param service: class|Service
            The service or service class to be registered.
        @param implementation: object
            The implementation for the provided service.
        '''
        
    @abc.abstractmethod
    def findResourcePath(self, converter, paths):
        '''
        Finds the resource node for the provided request path.
        
        @param converter: Converter
            The converter used in handling the path elements.
        @param paths: list
            A list of string path elements identifying a resource to be searched for.
        @return: Path
            The path leading to the node that provides the paths resource.
        '''