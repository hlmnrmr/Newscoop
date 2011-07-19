'''
Created on Jun 12, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the util module.
'''

import unittest
from ally.core.util import Singletone, Uninstantiable, guard, Protected
import builtins

# --------------------------------------------------------------------

class Single(Singletone):
    '''
    '''

class CannotCreate(Uninstantiable):
    '''
    '''

@guard
class Guarded:
    '''
    '''
    
    def __init__(self):
        self._attri = '100'
        
@guard
class OthModuleGuarded:
    '''
    '''
    
    def __init__(self):
        self._attri = '100'
        
class Protect(Protected):
    '''
    '''

class OthModuleProtect(Protected):
    '''
    '''
    
# --------------------------------------------------------------------

class TestUtil(unittest.TestCase):

    def testSucces(self):
        s1 = Singletone()
        s2 = Singletone()
        guard = Guarded()
        protect = Protect()
        
        self.assertTrue(s1 != s2)
        self.assertTrue(guard._attri == '100')
        guard.custom = 100
        self.assertTrue(guard.custom == 100)
        self.assertTrue(protect is not None)

    # ----------------------------------------------------------------
    
    def testFailed(self):
        s1 = Singletone()
        s2 = Singletone()
        guard = Guarded()
        othMod = OthModuleGuarded()
        OthModuleGuarded.__module__ = builtins
        OthModuleProtect.__module__ = builtins
        
        self.assertFalse(s1 == s2)
        
        self.assertRaises(AssertionError, CannotCreate)
        self.assertRaises(AssertionError, guard.__setattr__, '_attri', 20)
        self.assertRaises(AssertionError, othMod.__getattribute__, '_attri')
        self.assertRaises(AssertionError, OthModuleProtect.__new__, OthModuleProtect)
        
# --------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
