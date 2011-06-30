'''
Created on Jun 18, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Module containing specifications for the resources tree.
'''

from newscoop.core.api.type import Type
from newscoop.core.util import simpleName, guard
import abc

# --------------------------------------------------------------------

@guard
class Path:
    '''
    Provides the path container.
    The path is basically a immutable collection of matches. 
    '''
    
    def __init__(self, matches, node=None):
        '''
        Initializes the path.

        @param matches: list
            The list of matches that represent the path.
        @param node: Node
            The node represented by the path, if None it means that the path is incomplete.
        '''
        assert isinstance(matches, list), 'Invalid matches list %s' % matches
        assert node is None or isinstance(node, Node), 'Invalid node % can be None' % node
        if __debug__:
            for match in matches: assert isinstance(match, Match), 'Invalid match %s' % match
        self.matches = matches
        self.node = node
        
    def values(self):
        '''
        Provides the parameter values represented by this path.
        
        @return: list
            Return the list of parameters represented by the path, can be empty list if there are none.
        '''
        values = []
        for match in self.matches:
            assert isinstance(match, Match)
            value = match.value()
            if value is not None:
                if isinstance(value, list):
                    values.extend(value)
                values.append(value)
        return values
    
    def update(self, value):
        '''
        Updates all the matches in the path with the provided value.
        
        @param value: object
            The value to update with.
        @return: boolean
            True if at least a match has a successful update, false otherwise.
        '''
        sucess = False
        for match in self.matches:
            assert isinstance(match, Match)
            sucess |= match.update(value)
        return sucess

    def isValid(self):
        '''
        Checks if the path is valid, this means that the path will provide valid paths elements.
        
        @return: boolean
            True if the path can provide the paths, false otherwise.
        '''
        if self.node is not None:
            valid = True
            for match in self.matches:
                assert isinstance(match, Match)
                valid &= match.isValid()
            return valid
        return False
        
    def asPaths(self, converter):
        '''
        Converts the matches into a paths elements.
        
        @param converter: Converter
            The converter to use in constructing the paths elements.
        @return: list
            A list of strings representing the paths elements, or None if the path elements cannot be obtained.
        @raise AssertionError:
            If the path cannot be represented, check first the 'isValid' method.
        '''
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter
        paths = []
        for match in self.matches:
            assert isinstance(match, Match)
            path = match.asPath(converter)
            if isinstance(path, list):
                paths.extend(path)
            paths.append(path)
        return paths

@guard
class Assembler(metaclass=abc.ABCMeta):
    '''
    This class needs to be extended.
    Provides support for assembling the calls in the node structure.
    '''
    
    @abc.abstractmethod
    def assemble(self, root, invokers):
        '''
        Resolve in the provided root node the invokers, this means that the assembler needs to find a way of 
        mapping the invokers to a resource request path in the node structure contained in the root node 
        provided. If the assembler is able to resolve a invoker or invokers it has to remove them from the list.
        
        @param root: Node
            The root node to assemble the invokers to.
        @param invokers: list
            The list of invokers to be assembled.
        '''

@guard
class Converter(metaclass=abc.ABCMeta):
    '''
    Provides the conversion of primitive types to strings in vice versa.
    The converter provides basic conversion, please extend for more complex or custom transformation.
    '''
    
    @abc.abstractmethod
    def normalize(self, value):
        '''
        Normalizes the provided string value as seen fit by the converter.
        The main condition is that the normalized has to be the same for the same value.
        
        @param value: string
            The string value to be normalized.
        @return: string
            The normalized string.
        '''
    
    @abc.abstractmethod
    def asString(self, objValue):
        '''
        Converts the provided object to a string. First it will detect the type and based on that it will call
        the corresponding convert method.
        
        @param objValue: object
            The value to be converted to string.
        @return: string
            The string form of the provided value object.
        '''
    
    @abc.abstractmethod
    def convertBool(self, boolValue=None, parse=None):
        '''
        Converts an boolean to a string or a string to boolean depending on the provided value.
        Only one of the parameters need to be specified.
        
        @param boolValue: boolean
            The boolean value to be converted to string.
        @param parse: string
            The value to be parsed as an boolean.
        @return: boolean|string
            Depending on the provided parameter it will provide either a parsed boolean or string of the 
            provided boolean.
        @raise ValueError: In case the parsing was not successful.
        '''
    
    @abc.abstractmethod
    def convertInt(self, intValue=None, parse=None):
        '''
        Converts an integer to a string or a string to integer depending on the provided value.
        Only one of the parameters need to be specified.
        
        @param intValue: integer
            The integer value to be converted to string.
        @param parse: string
            The value to be parsed as an integer.
        @return: integer|string
            Depending on the provided parameter it will provide either a parsed integer or string of the 
            provided integer.
        @raise ValueError: In case the parsing was not successful.
        '''
    
    @abc.abstractmethod
    def convertDecimal(self, decValue=None, parse=None):
        '''
        Converts a decimal to a string or a string to decimal depending on the provided value.
        Only one of the parameters need to be specified.
        
        @param decValue: float
            The decimal value to be converted to string.
        @param parse: string
            The value to be parsed as an decimal.
        @return: decimal|string
            Depending on the provided parameter it will provide either a parsed decimal or string of the 
            provided decimal.
        @raise ValueError: In case the parsing was not successful.
        '''

@guard
class Match(metaclass=abc.ABCMeta):
    '''
    Provides a matched path entry.
    '''
    
    def __init__(self, node):
        '''
        Constructs a match.
        
        @param node: Node
            The Node node of the match.
        '''
        assert isinstance(node, Node), 'Invalid node %s' % node
        self.node = node
    
    @abc.abstractmethod
    def value(self):
        '''
        Provides the parameter represented by this match.
        
        @return: object|list|None
            Return the parameter or list of parameters represented by the match, None if the match is not 
            providing any parameter.
        '''
    
    @abc.abstractmethod
    def update(self, value):
        '''
        Updates the match represented value.
        
        @param value: object
            The value to update with.
        @return: boolean
            True if the updated was successful, false otherwise.
        '''
    
    @abc.abstractmethod
    def isValid(self):
        '''
        Checks if the match is valid, this means that the match will provide a valid path element.
        
        @return: boolean
            True if the match can provide a path, false otherwise.
        '''
    
    @abc.abstractmethod
    def asPath(self, converter):
        '''
        Converts the match into a path or paths elements.
        
        @param converter: Converter
            The converter to use in constructing the path(s) elements.
        @return: string|list
            A string or list of strings representing the path element.
        @raise AssertionError:
            If the path cannot be represented, check first the 'isValid' method.
        '''
        
    @abc.abstractmethod
    def __eq__(self, other):
        '''
        Needs to have the equal implemented.
        '''

@guard
class Invoker(metaclass=abc.ABCMeta):
    '''
    Contains all the data required for accessing a call.
    '''
    
    def __init__(self, outputType, name, inputTypes, mandatoryCount):
        '''
        Constructs an invoker.
        
        @param outputType: Type
            The output type of the invoker.
        @param name: string
            The name of the invoker.
        @param inputTypes: list
            The list of input Type(s) for the invoker, attention not all input types are mandatory.
        @param mandatoryCount: integer
            Provides the count of the mandatory input types, if the mandatory count is two and we have three input
            types it means that just the first two parameters need to be provided.
        '''
        assert isinstance(outputType, Type), 'Invalid output type %s' % outputType
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(inputTypes, list), 'Invalid input types list %s' % inputTypes
        assert isinstance(mandatoryCount, int), 'Invalid mandatory count <%s>, needs to be integer' % mandatoryCount
        assert mandatoryCount >= 0 and mandatoryCount <= len(inputTypes), \
        'Invalid mandatory count <%s>, needs to be greater than 0 and less than ' % (mandatoryCount, len(inputTypes))
        if __debug__:
            for typ in inputTypes:
                assert isinstance(typ, Type), 'Invalid input type %s' % typ
        self.outputType = outputType
        self.name = name
        self.inputTypes = inputTypes
        self.mandatoryCount = mandatoryCount
    
    @abc.abstractmethod
    def invoke(self, *args):
        '''
        Make the invoking and return the resources.
        
        @param args: tuple
            The arguments to use in invoking.
        '''

    def __str__(self):
        inputStr = []
        for i, typ in enumerate(self.inputTypes):
            inputStr.append(('defaulted:' if i >= self.mandatoryCount else '') + str(typ))
        return '<%s[%s %s(%s)]>' % (simpleName(self), self.outputType, self.name, ', '.join(inputStr))

@guard(ifNoneSet=('get', 'insert', 'update', 'delete'))
class Node(metaclass=abc.ABCMeta):
    '''
    The resource node provides searches and info for resource request paths. Also provides the ability to 
    acknowledge a path(s) as belonging to the node. All nodes implementations need to be exclusive by nature, 
    meaning that not two nodes should be valid for the same path.
    '''
    
    def __init__(self, parent, order):
        '''
        Constructs a resource node. 
        
        @param parent: Node|None 
            The parent node of this node, can be None if is a root node.
        @param order: integer 
            The order index of the node, this will be used in correctly ordering the children's to have a proper
            order when searching for path matching.
        @ivar get: Invoker
            The invoker that provides the retrieve of elements, populated by assemblers.
        @ivar insert: Invoker
            The invoker that provides the insert of elements, populated by assemblers.
        @ivar update: Invoker
            The invoker that provides the update of elements, populated by assemblers.
        @ivar delete: Invoker
            The invoker that provides the deletion of elements, populated by assemblers.
         @ivar _childrens: list
            The list of node children's.
        '''
        assert parent is None or isinstance(parent, Node), 'Invalid parent %s, can be None' % parent
        assert isinstance(order, int), 'Invalid order %s' % order
        self.parent = parent
        self.order = order
        self.get = None
        self.insert = None
        self.update = None
        self.delete = None
        self._childrens = []
        if parent is not None:
            parent.addChild(self)
        
    def addChild(self, child):
        '''
        Adds a new child node to this node.
        
        @param child: Node
            The new child node to add.
        '''
        assert isinstance(child, Node), 'Invalid child node %s' % child
        assert child.parent is self, 'The child has a different parent %s' % child
        assert child not in self._childrens, 'Already contains children node %s' % child
        self._childrens.append(child)
        self._childrens.sort(key=lambda node: node.order)

    def childrens(self):
        '''
        Provides a list with all the children's of the node.
        
        @return: list
            The list of children nodes.
        '''
        return self._childrens
    
    @abc.abstractmethod
    def tryMatch(self, converter, paths):
        '''
        Override to provide functionality.
        Checks if the path(s) element is a match, in this case the paths list needs to be trimmed of the path
        elements that have been acknowledged by this node.
        
        @param converter: Converter
            The converter to be used in matching the provided path(s).
        @param paths: list
            The path elements list, this list will get consume whenever a matching occurs.
        @return: Match|list|boolean
            If a match has occurred than a match or a list with match objects will be returned or True if there
            is no match to provide by this node, if not than None or False is returned.
        '''
    
    @abc.abstractmethod
    def newMatch(self):
        '''
        Override to provide functionality.
        Constructs a blank match object represented by this node, this is used in creating path for nodes.
        So basically this used when we need a path for a node.
        
        @return: Match|list|None
            A match object or a list with match objects, None if there is no match needed by this node.
        '''
    
    @abc.abstractmethod
    def __eq__(self, other):
        '''
        Needs to have the equal implemented.
        '''
