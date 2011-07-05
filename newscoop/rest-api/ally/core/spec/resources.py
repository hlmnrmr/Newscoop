'''
Created on Jun 18, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing specifications for the resources tree.
'''

from ally.core.api.type import Type, Input
from ally.core.util import simpleName, guard
import abc
import numbers
from inspect import isclass

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
        
    def toArguments(self):
        '''
        Provides the list of arguments contained in this path.
        
        @return: dictionary
            Return the dictionary of arguments of this path the key is the name of the argument, can be empty list
            if there are no arguments.
        '''
        args = {}
        for match in self.matches:
            assert isinstance(match, Match)
            match.asArgument(args)
        return args
    
    def update(self, obj, objType):
        '''
        Updates all the matches in the path with the provided value. This method looks like a render method 
        expecting value and type, this because the path is actually a renderer for the paths elements.
        
        @param obj: object
            The object value to update with.
        @param objType: Type
            The object type.
        @return: boolean
            True if at least a match has a successful update, false otherwise.
        '''
        sucess = False
        for match in self.matches:
            assert isinstance(match, Match)
            sucess |= match.update(obj, objType)
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
    
    def asString(self, objValue):
        '''
        Converts the provided object to a string. First it will detect the type and based on that it will call
        the corresponding convert method.
        
        @param objValue: object
            The value to be converted to string.
        @return: string
            The string form of the provided value object.
        '''
        assert objValue is not None, 'No object value is provided'
        if isinstance(objValue, str):
            return objValue
        if isinstance(objValue, bool):
            return self.convertBool(objValue)
        if isinstance(objValue, int):
            return self.convertInt(objValue)
        if isinstance(objValue, numbers.Number):
            return self.convertInt(objValue)
        raise AssertionError('Invalid object value %s' % objValue)
        
    def asValue(self, strValue, objType):
        '''
        Parses the string value into an object value depending on the provided object type.
        
        @param strValue: string
            The string representation of the object to be parsed.
        @param objType: class
            The type of object to which the string should be parsed.
        @raise ValueError: In case the parsing was not successful.
        '''
        assert isinstance(strValue, str), 'Invalid string value %s' % strValue
        assert isclass(objType), 'Invalid object type %s' % objType
        if objType == str:
            return strValue
        if objType == bool:
            return self.convertBool(parse=strValue)
        if objType == int:
            return self.convertInt(parse=strValue)
        if objType == numbers.Number:
            return self.convertInt(parse=strValue)
        raise AssertionError('Invalid object type %s' % objType)
    
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
    def asArgument(self, args):
        '''
        Populates in the provided dictionary of arguments, the key represents the argument name.
        
        @param args: dictionary
            The dictionary where the argument(s) name and value(s) of this match will be populated.
        '''
    
    @abc.abstractmethod
    def update(self, obj, objType):
        '''
        Updates the match represented value. This method looks like a render method expecting value and type,
        this because the match is actually a renderer for path elements.
        
        @param obj: object
            The object value to update with.
        @param objType: Type
            The object type.
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
    
    def __init__(self, outputType, name, inputs, mandatoryCount):
        '''
        Constructs an invoker.
        
        @param outputType: Type
            The output type of the invoker.
        @param name: string
            The name of the invoker.
        @param inputs: list
            The list of Inputs for the invoker, attention not all inputs are mandatory.
        @param mandatoryCount: integer
            Provides the count of the mandatory input types, if the mandatory count is two and we have three input
            types it means that just the first two parameters need to be provided.
        '''
        assert isinstance(outputType, Type), 'Invalid output type %s' % outputType
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(inputs, list), 'Invalid inputs list %s' % inputs
        assert isinstance(mandatoryCount, int), 'Invalid mandatory count <%s>, needs to be integer' % mandatoryCount
        assert mandatoryCount >= 0 and mandatoryCount <= len(inputs), \
        'Invalid mandatory count <%s>, needs to be greater than 0 and less than ' % (mandatoryCount, len(inputs))
        if __debug__:
            for inp in inputs:
                assert isinstance(inp, Input), 'Invalid input %s' % inp
        self.outputType = outputType
        self.name = name
        self.inputs = inputs
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
        for i, inp in enumerate(self.inputs):
            inputStr.append(('defaulted:' if i >= self.mandatoryCount else '') + inp.name + '=' + str(inp.type))
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
            The path elements list containing strings, this list will get consumed whenever a matching occurs.
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
    
    @abc.abstractmethod
    def findAllPaths(self, outputType, *inputTypes):
        '''
        Finds all the resource nodes that has a get method having the provided input type(s).
        
        @param outputType: Type|None
            The output type to locate the path for, None if not required.
        @param inputTypes: tuple
            The input types tuple to locate the path for.
        @return: list
            A list of paths leading to the nodes having a get method with the requested input type(s), might be
            empty if no such nodes exist.
        '''

    @abc.abstractmethod
    def findShortPath(self, outputType, *inputTypes):
        '''
        Finds the resource node that has a get method having the provided input type(s) that is has the shortest
        path leading to it.
        
        @param outputType: Type|None
            The output type to locate the path for, None if not required.
        @param inputTypes: tuple
            The input types tuple to locate the path for.
        @return: Path|None
            The shortest path leading to the node or None if no node is found.
        '''
