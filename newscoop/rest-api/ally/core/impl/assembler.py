'''
Created on Jun 18, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the call assemblers used in constructing the resources node.
'''

from ally.core.api.type import TypeProperty, TypeModel, TypeId, Iter, Input
from ally.core.impl.node import NodeModel, NodeId
from ally.core.spec.resources import Assembler, Node, Invoker
import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class AssembleInvokers(Assembler):
    '''
    Provides support for assemblers that want to do the assembling on an invoker at one time.
    '''
        
    def assemble(self, root, invokers):
        '''
        @see: Assembler.resolve
        '''
        k = 0
        while k < len(invokers):
            if self.assembleInvoke(root, invokers[k]):
                del invokers[k]
            else: k += 1
    
    @abc.abstractmethod
    def assembleInvoke(self, root, invoker):
        '''
        Provides the assembling for a single invoker.
        
        @param root: Node
            The root node to assemble the invokers to.
        @param invoker: Invoker
            The invoker to be assembled.
        @return: boolean
            True if the assembling has been successful, False otherwise.
        '''

# --------------------------------------------------------------------
          
class AssembleGetAll(AssembleInvokers):
    '''
    Resolving the get all for models.
    '''
        
    def assembleInvoke(self, root, invoker):
        '''
        @see: AssembleInvokers.resolve
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        if not (isinstance(invoker.outputType, Iter) and invoker.mandatoryCount == 0):
            return False
        typ = invoker.outputType.itemType
        if isinstance(typ, TypeModel):
            model = typ.model
        elif isinstance(typ, TypeProperty) and isinstance(typ.property.type, TypeId):
            model = typ.model
        else:
            return False
        node = _obtainNodeModel(root, model)
        assert node.get is None, 'There is already a get assigned for %' % node
        node.get = invoker
        log.info('Resolved invoker %s as a get all for model %s', invoker, model)
        return True

class AssembleGetById(AssembleInvokers):
    '''
    Resolving the get by id for models.
    '''
        
    def assembleInvoke(self, root, invoker):
        '''
        @see: AssembleInvokers.resolve
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        if not isinstance(invoker.outputType, TypeModel):
            return False
        model = invoker.outputType.model
        if not(len(invoker.inputs) > 0 and invoker.mandatoryCount == 1):
            return False
        inputId = invoker.inputs[0]
        assert isinstance(inputId, Input)
        typeProperty = inputId.type
        if not(isinstance(typeProperty, TypeProperty) and isinstance(typeProperty.property.type, TypeId)):
            return False
        if not(typeProperty.model == model and typeProperty.forClass() == int):
            return False
        node = _obtainNodeModel(root, model)
        node = _obtainNodeId(node, inputId)
        assert node.get is None, 'There is already a get assigned for %' % node
        node.get = invoker
        log.info('Resolved invoker %s as a get by id for model %s', invoker, model)
        return True

# --------------------------------------------------------------------

def _obtainNodeModel(root, model):
    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodeModel) and child.model == model:
            return child
    return NodeModel(root, model)

def _obtainNodeId(root, inputId):
    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodeId) and child.inputId == inputId:
            return child
    return NodeId(root, inputId)
