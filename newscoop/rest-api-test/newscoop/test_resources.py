'''
Created on Jun 19, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the resource module.
'''

#from ally.core import util
#util.GUARD_ENABLED = False
import logging
from ally.core.impl.resources_manager import ResourcesManagerImpl
from ally.core.impl.assembler import ASSEMBLERS
logging.basicConfig(level=logging.DEBUG)

import unittest
from newscoop.api import publication, resource, theme

# --------------------------------------------------------------------

class Test(unittest.TestCase):

    def testSuccesQuery(self):
        rscManager = ResourcesManagerImpl(ASSEMBLERS)
        rscManager.register(publication.IPublicationService, None)
        rscManager.register(resource.IResourceService, None)
        rscManager.register(theme.IThemeService, None)
        
# --------------------------------------------------------------------
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
