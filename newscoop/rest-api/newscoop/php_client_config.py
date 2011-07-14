'''
Created on Jul 3, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides additional configurations for the Zend PHP client.
'''

from ally.core.spec import content_type as ct
from newscoop.service_config import server_config as sc

# --------------------------------------------------------------------

def setupAll():
    sc.contentTypes[ct.JSON].append('application/x-www-form-urlencoded')
