'''
Created on Jun 19, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the nodes used in constructing the resources node tree.
'''

from ally.core.api.operator import Model
from ally.core.api.type import TypeProperty, TypeId, Type, TypeModel, Input
from ally.core.spec.resources import Converter, Match, Node, Invoker
from ally.core.util import simpleName
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

ORDER_ROOT = 0
ORDER_STRING = 1
ORDER_INTEGER = 2

# --------------------------------------------------------------------

class MatchString(Match):
    '''
    Match class for string.
    
    @see: Match
    '''
    
    def __init__(self, node, matchValue):
        '''
        @see: Match.__init__
        
        @param matchValue: string
            The string value of the match.
        '''
        super().__init__(node)
        assert isinstance(matchValue, str), 'Invalid string match value %s' % matchValue
        self.matchValue = matchValue
    
    def asArgument(self, args):
        '''
        @see: Match.asArgument
        '''
        # Nothing to do here
    
    def isValid(self):
        '''
        @see: Match.isValid
        '''
        return True
    
    def update(self, obj, objType):
        '''
        @see: Match.update
        '''
        return False
    
    def asPath(self, converter):
        '''
        @see: Match.asPath
        '''
        assert isinstance(converter, Converter)
        return converter.normalize(self.matchValue)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.matchValue == other.matchValue
        return False

class MatchId(Match):
    '''
    Match class for @see NodeId.
    
    @see: Match
    '''
    
    def __init__(self, node, matchValue=None):
        '''
        @see: Match.__init__
        
        @param matchValue: integer|None
            The match integer value, none if the match will expect updates.
        '''
        assert isinstance(node, NodeId), 'Invalid node %s needs to be node on type property id' % node
        super().__init__(node)
        assert matchValue is None or isinstance(matchValue, int), \
        'Invalid match integer value %s, can be None' % matchValue
        self.matchValue = matchValue
    
    def asArgument(self, args):
        '''
        @see: Match.value
        '''
        assert isinstance(args, dict), 'Invalid arguments dictionary %s' % args
        assert self.matchValue != None, 'This match %s has not value' % self
        args[self.node.inputId.name] = self.matchValue
    
    def update(self, obj, objType):
        '''
        @see: Match.update
        '''
        assert isinstance(objType, Type), 'Invalid object type %s' % objType
        if isinstance(objType, TypeModel):
            assert isinstance(objType, TypeModel)
            if objType.model == self.node.inputId.type.model:
                self.matchValue = self.node.inputId.type.property.get(obj)
                return True
        elif isinstance(objType, TypeProperty):
            if objType == self.node.inputId.type:
                self.matchValue = obj
                return True
        return False
    
    def isValid(self):
        '''
        @see: Match.isValid
        '''
        return self.matchValue is not None
    
    def asPath(self, converter):
        '''
        @see: Match.asPath
        '''
        assert isinstance(converter, Converter)
        assert self.matchValue is not None, 'Cannot represent the path element, there is no value'
        return converter.asString(self.matchValue)
    
    def __eq__(self, other):
        return isinstance(other, MatchId)

# --------------------------------------------------------------------

class NodeRoot(Node):
    '''
    Provides a node for the root.
    
    @see: Node
    '''
    
    def __init__(self, get):
        '''
        @see: Match.__init__
        
        @param get: Invoker
            The get invoker for the root node.
        '''
        super().__init__(None, ORDER_ROOT)
        assert isinstance(get, Invoker), 'Invalid get invoker %s' % get
        assert len(get.inputs) == 0, 'No inputs are allowed for the get on the root node'
        self.get = get

    def tryMatch(self, converter, paths):
        '''
        @see: Matcher.tryMatch
        '''
        return True

    def newMatch(self):
        '''
        @see: Matcher.newMatch
        '''
        return None

    def __eq__(self, other):
        return isinstance(other, self.__class__)
    
    def __str__(self):
        return '<Node Root>'

# --------------------------------------------------------------------

class NodeModel(Node):
    '''
    Provides a node that matches model elements.
    
    @see: Node
    '''
    
    def __init__(self, parent, model):
        '''
        @see: Node.__init__
        
        @param model: Model
            The model to make the matching based on.
        @ivar _match: MatchString
            The match corresponding to this node.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        self.model = model
        self._match = MatchString(self, model.name)
        super().__init__(parent, ORDER_STRING)

    def tryMatch(self, converter, paths):
        '''
        @see: Matcher.tryMatch
        '''
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter
        assert isinstance(paths, list), 'Invalid paths %s' % paths
        assert len(paths) > 0, 'No path element in paths %s' % paths
        if converter.normalize(self._match.matchValue) == paths[0]:
            del paths[0]
            return self._match
        return None

    def newMatch(self):
        '''
        @see: Matcher.newMatch
        '''
        return self._match

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.model == other.model
        return False
    
    def __str__(self):
        return '<%s[%s]>' % (simpleName(self), self.model)

class NodeId(Node):
    '''
    Provides a node based on a type property id.
    
    @see: Node
    '''
    
    def __init__(self, parent, inputId):
        '''
        @see: Node.__init__
        
        @param inputId: Input
            The input with type property represented by the node.
        '''
        assert isinstance(inputId, Input), 'Invalid input %s' % inputId
        assert isinstance(inputId.type, TypeProperty), 'Invalid input type property %s' % inputId.type
        assert isinstance(inputId.type.property.type, TypeId), \
        'Invalid property type %s needs to be a type id' % inputId.type.property.type
        assert inputId.type.forClass() == int, \
        'Invalid type id class %s needs to be integer' % inputId.type.forClass()
        self.inputId = inputId
        super().__init__(parent, ORDER_INTEGER)

    def tryMatch(self, converter, paths):
        '''
        @see: Matcher.tryMatch
        '''
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter
        assert isinstance(paths, list), 'Invalid paths %s' % paths
        assert len(paths) > 0, 'No path element in paths %s' % paths
        try:
            value = converter.convertInt(parse=paths[0])
            del paths[0]
            return MatchId(self, value)
        except ValueError:
            return None

    def newMatch(self):
        '''
        @see: Matcher.newMatch
        '''
        return MatchId(self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.inputId == other.inputId
        return False

    def __str__(self):
        return '<%s[%s]>' % (simpleName(self), self.inputId)
