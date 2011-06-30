'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides renders implementations.
'''
from newscoop.core.api.type import List, TypeModel
from newscoop.core.spec.server import Encoder
from newscoop.core.spec.resources import Path

# --------------------------------------------------------------------

# --------------------------------------------------------------------

def forListPath(obj, objType, encoder):
    assert isinstance(encoder, Encoder)
    if isinstance(objType, List):
        assert isinstance(objType, List)
        if isinstance(objType.itemType, Path):
        encoder.open(name)
        for item in obj:
            
        objType.itemType
        return True
    return False