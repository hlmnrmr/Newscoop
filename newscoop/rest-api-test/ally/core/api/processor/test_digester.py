'''
Created on Jul 13, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the digester module.
'''

from ally.core import util
util.GUARD_ENABLED = False
import logging
logging.basicConfig(level=logging.DEBUG)

from ally.core.api.configure import propertiesFor, APIModel, APIProperty
from ally.core.impl.converter import Standard
from ally.core.impl.processor.encdec_xml import Digester, RuleRoot, RuleModel, \
    RuleSetProperty
from io import BytesIO
import unittest

# --------------------------------------------------------------------

@APIModel()
class Entity:
    
    id = APIProperty(int)
    
    x = float

# --------------------------------------------------------------------

class TestDigester(unittest.TestCase):

    def testSucces(self):
        root = RuleRoot()
        model = propertiesFor(Entity)
        bean = root.addRule(RuleModel(model), 'MyBean')
        bean.addRule(RuleSetProperty(model.properties['id'], None, Standard()), 'Id')
        bean.addRule(RuleSetProperty(model.properties['x'], None, Standard()), 'Name')
        
        dig = Digester(root)
        pub = dig.parse('utf-8', BytesIO(b'''<MyBean><Id>3</Id><Name>100.2</Name></MyBean>'''))
        
        self.assertTrue(pub is not None)
        self.assertTrue(pub.id == 3)
        self.assertTrue(pub.x == 100.2)

    # ----------------------------------------------------------------
    
    def testFailed(self):
        pass
    
# --------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
