'''
Created on Jun 18, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the call assemblers used in constructing the resources node.
'''

from inspect import isfunction, getargspec
from ally.core.api.type import TypeProperty, TypeModel, TypeId, List, \
    TypeQuery
from ally.core.impl.node import NodeModel, NodeTypePropertyId
from ally.core.spec.resources import Assembler, Node, Invoker
import logging
import sys

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class OnFunction(Assembler):
    '''
    Assembler based on a function that will do the assembling work.
    '''

    def __init__(self, function):
        '''
        Constructs the on function assembler based on the provided function.
        
        @param function: function
            The function doing the assembling work.
        '''
        assert isfunction(function), 'Invalid function provided %s' % function
        self.function = function
        
    def assemble(self, root, invokers):
        '''
        @see: Assembler.resolve
        '''
        k = 0
        while k < len(invokers):
            if self.function(root, invokers[k]):
                del invokers[k]
            else: k += 1

# --------------------------------------------------------------------

def checModelType(typ, model):
    return isinstance(typ, TypeModel) and typ.model == model

def checPropertyIdType(typ, model):
    return isinstance(typ, TypeProperty) and typ.model == model  and isinstance(typ.property.type, TypeId)

def checHasQueryType(typs, query):
    for typ in typs:
        if isinstance(typ, TypeQuery) and typ.query == query:
            return True
    return False

# --------------------------------------------------------------------

def obtainNodeModel(root, model):
    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodeModel) and child.model == model:
            return child
    return NodeModel(root, model)

def obtainNodeTypePropertyId(root, typeProperty):
    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodeTypePropertyId) and child.typeProperty == typeProperty:
            return child
    return NodeTypePropertyId(root, typeProperty)
        
# --------------------------------------------------------------------

def forGetAll(root, invoker):
    '''
    Resolving the get all for models.
    '''
    assert isinstance(root, Node), 'Invalid node %s' % root
    assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
    if not (isinstance(invoker.outputType, List) and invoker.mandatoryCount == 0):
        return False
    typ = invoker.outputType.itemType
    if isinstance(typ, TypeModel):
        model = typ.model
    elif isinstance(typ, TypeProperty) and isinstance(typ.property.type, TypeId):
        model = typ.model
    else:
        return False
    node = obtainNodeModel(root, model)
    assert node.get is None, 'There is already a get assigned for %' % node
    node.get = invoker
    log.info('Resolved invoker %s as a get all for model %s', invoker, model)
    return True

def forGetById(root, invoker):
    '''
    Resolving the get by id for models.
    '''
    assert isinstance(root, Node), 'Invalid node %s' % root
    assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
    if not isinstance(invoker.outputType, TypeModel):
        return False
    model = invoker.outputType.model
    if not(len(invoker.inputTypes) > 0 and invoker.mandatoryCount == 1):
        return False
    typeProperty = invoker.inputTypes[0]
    if not(isinstance(typeProperty, TypeProperty) and isinstance(typeProperty.property.type, TypeId)):
        return False
    if not(typeProperty.model == model and typeProperty.property.type.forClass == int):
        return False
    node = obtainNodeModel(root, model)
    node = obtainNodeTypePropertyId(node, typeProperty)
    assert node.get is None, 'There is already a get assigned for %' % node
    node.get = invoker
    log.info('Resolved invoker %s as a get by id for model %s', invoker, model)
    return True

# --------------------------------------------------------------------

def __assemblers():
    '''
    FOR INTERNAL USE ONLY.
    Provides the assemblers constructed based on specific functions in this module.
    '''
    asms = []
    module = sys.modules[__name__]
    for name in dir(module):
        func = module.__dict__[name]
        if isfunction(func) and func.__name__.startswith('for') and len(getargspec(func).args) == 2:
            asms.append(OnFunction(func))
            log.info('Added assembler for function %s', func.__name__)
    return asms

# Contains all the assemblers to be used for calls
ASSEMBLERS = __assemblers()

# --------------------------------------------------------------------
