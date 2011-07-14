'''
Created on Jun 18, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the call assemblers used in constructing the resources node.
'''

from ally.core.api.type import TypeProperty, TypeModel, TypeId, Iter, Input,\
    isPropertyTypeId
from ally.core.impl.node import NodeModel, NodeId
from ally.core.spec.resources import Assembler, Node, Invoker
import abc
import logging
from ally.core.api.operator import Model, Property

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class InvokerUpdateModel(Invoker):
    '''
    Wraps an update invoker that has the signature like bool%(Entity) to look like bool%(Entity.Id, Entity) which
    is the form that is called by the delete action.
    '''
    
    def __init__(self, invoker, typeProperty):
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(typeProperty, TypeProperty), 'Invalid type property %s' % typeProperty
        modelInput = invoker.inputs[0]
        inputs = [Input(modelInput.name + 'Id', typeProperty), modelInput]
        super().__init__(invoker.outputType, invoker.name, inputs, len(inputs))
        self.invoker = invoker
        self.property = typeProperty.property
        
    def invoke(self, *args):
        '''
        First argument is the id and the second the entity.
        @see: Invoker.invoke
        '''
        prop = self.property
        assert isinstance(prop, Property)
        prop.set(args[1], args[0])
        return self.invoker.invoke(args[1])

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
    Resolving the get all for models, methods presentation: Iter(Entity.Id)%(,[defaults])
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
    Resolving the get by id for models, methods presentation: Entity%(Entity.Id)
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
        if not isPropertyTypeId(invoker.inputs[0].type, model):
            return False
        node = _obtainNodeId(_obtainNodeModel(root, model), invoker.inputs[0].type)
        assert node.get is None, 'There is already a get assigned for %' % node
        node.get = invoker
        log.info('Resolved invoker %s as a get by id for model %s', invoker, model)
        return True
    
class AssembleInsert(AssembleInvokers):
    '''
    Resolving the insert for models, methods presentation: [Entity.Id|Entity]%(Entity)
    '''
        
    def assembleInvoke(self, root, invoker):
        '''
        @see: AssembleInvokers.resolve
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        if len(invoker.inputs) != 1:
            return False
        if not isinstance(invoker.inputs[0].type, TypeModel):
            return False
        model = invoker.inputs[0].type.model
        if isinstance(invoker.outputType, TypeProperty):
            if not isPropertyTypeId(invoker.outputType, model):
                return False
        elif isinstance(invoker.outputType, TypeModel):
            if not model == invoker.outputType.model:
                return False
        else: return False
        node = _obtainNodeModel(root, model)
        assert node.insert is None, 'There is already an insert assigned for %' % node
        node.insert = invoker
        log.info('Resolved invoker %s as an insert for model %s', invoker, model)
        return True

class AssembleUpdateIdModel(AssembleInvokers):
    '''
    Resolving the update for models, methods presentation: bool%(Entity.Id, Entity).
    '''
        
    def assembleInvoke(self, root, invoker):
        '''
        @see: AssembleInvokers.resolve
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        if not len(invoker.inputs) == 2:
            return False
        if not isinstance(invoker.inputs[1].type, TypeModel):
            return False
        model = invoker.inputs[1].type.model
        if not isPropertyTypeId(invoker.inputs[0].type, model):
            return False
        if invoker.outputType.forClass() != bool:
            return False
        node = _obtainNodeId(_obtainNodeModel(root, model), invoker.inputs[0].type)
        assert node.update is None, 'There is already an update assigned for %' % node
        node.update = invoker
        log.info('Resolved invoker %s as an update for id model %s', invoker, model)
        return True
    
class AssembleUpdateModel(AssembleInvokers):
    '''
    Resolving the update for models, methods presentation: bool%(Entity).
    '''
        
    def assembleInvoke(self, root, invoker):
        '''
        @see: AssembleInvokers.resolve
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        if not len(invoker.inputs) == 1:
            return False
        if not isinstance(invoker.inputs[0].type, TypeModel):
            return False
        model = invoker.inputs[0].type.model
        assert isinstance(model, Model)
        if invoker.outputType.forClass() != bool:
            return False
        # finding the model id.
        propertyId = None
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            if isinstance(prop.type, TypeId) and prop.type.forClass() == int:
                propertyId = prop
                break
        if propertyId is None:
            log.warning('No property id found for model %s, so I cannot perform update', model)
            return False
        assert isinstance(propertyId, Property)
        typeProperty = TypeProperty(model, propertyId)
        node = _obtainNodeId(_obtainNodeModel(root, model), typeProperty)
        assert node.update is None, 'There is already an update assigned for %' % node
        node.update = InvokerUpdateModel(invoker, typeProperty)
        log.info('Resolved invoker %s as an update for model %s', invoker, model)
        return True
    
class AssembleDelete(AssembleInvokers):
    '''
    Resolving the delete for models.
    '''
        
    def assembleInvoke(self, root, invoker):
        '''
        @see: AssembleInvokers.resolve
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        if not len(invoker.inputs) == 1:
            return False
        if not isPropertyTypeId(invoker.inputs[0].type):
            return False
        typeId = invoker.inputs[0].type
        assert isinstance(typeId, TypeProperty)
        if invoker.outputType.forClass() != bool:
            return False
        node = _obtainNodeId(_obtainNodeModel(root, typeId.model), typeId)
        assert node.delete is None, 'There is already a delete assigned for %' % node
        node.delete = invoker
        log.info('Resolved invoker %s as a delete for model %s', invoker, typeId.model)
        return True

# --------------------------------------------------------------------

def _obtainNodeModel(root, model):
    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodeModel) and child.model == model:
            return child
    return NodeModel(root, model)

def _obtainNodeId(root, typeId):
    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodeId) and child.typeId == typeId:
            return child
    return NodeId(root, typeId)
