'''
Created on Jul 3, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters handler.
'''

from ally.core.api.type import Input, Type, Iter
from ally.core.internationalization import msg as _
from ally.core.spec.codes import ILLEGAL_PARAM
from ally.core.spec.resources import Node, Invoker, Converter
from ally.core.spec.server import Processor, ProcessorsChain, RequestResource, \
    Response, GET
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class ParametersHandler(Processor):
    '''
    Implementation for a processor that provides the transformation of parameters into arguments, if this is required.
    '''
    
    converter = Converter
    # The converter used in parsing the parameter values.    
    allValue = '*'
    # Used in marking the all values in parameters.
    
    def process(self, requestResource, responseAny, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        response = self.findResponseIn(responseAny)
        if isinstance(requestResource, RequestResource) and requestResource.request.method == GET \
        and len(requestResource.parameters) > 0 and response is not None:
            assert isinstance(requestResource, RequestResource)
            assert isinstance(response, Response)
            node = requestResource.path.node
            assert isinstance(node, Node), \
            'The node has to be available in the path %s problems in previous processors' % requestResource.path
            if node.get is not None:
                invoker = node.get
                assert isinstance(invoker, Invoker)
                # We only consider as parameters the not mandatory primitive inputs.
                for k in range(invoker.mandatoryCount, len(invoker.inputs)):
                    inp = invoker.inputs[k]
                    assert isinstance(inp, Input)
                    typ = inp.type
                    isList = False
                    # Need to check if is not a list.
                    if isinstance(typ, Iter):
                        typ = typ.itemType
                        isList = True
                    assert isinstance(typ, Type)
                    if not typ.isPrimitive:
                        continue
                    typ = typ.forClass()
                    params = []
                    k = 0
                    while k < len(requestResource.parameters):
                        if requestResource.parameters[k][0] == inp.name:
                            params.append(requestResource.parameters[k])
                            del requestResource.parameters[k]
                            k -= 1
                        k += 1
                    if len(params) > 1:
                        if not isList:
                            response.setCode(ILLEGAL_PARAM, _('Parameter ($1) needs to be provided just once', inp.name))
                            log.warning('To many parameters of name %s for %s', inp.name, requestResource.parameters)
                            return
                        values = []
                        for param in params:
                            if param[1] is None:
                                response.setCode(ILLEGAL_PARAM, _('Parameter ($1) needs to have a value', inp.name))
                                log.warning('No value for parameter %s', inp.name)
                                return
                            values.append(self.converter.asValue(param[1], typ))
                        requestResource.arguments[inp.name] = values
                    elif len(params) == 1:
                        value = params[0][1]
                        if value is None:
                            response.setCode(ILLEGAL_PARAM, _('Parameter ($1) needs to have a value', inp.name))
                            log.warning('No value for parameter %s', inp.name)
                            return
                        if value != '*':
                            requestResource.arguments[inp.name] = self.converter.asValue(value, typ)
        chain.process(requestResource, responseAny)
