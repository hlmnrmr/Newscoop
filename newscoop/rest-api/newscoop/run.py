'''
Created on Jul 6, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Used for starting the web server.
'''

# --------------------------------------------------------------------
from ally.core import util
util.GUARD_ENABLED = False
import logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARN)
#logging.basicConfig(level=logging.DEBUG)

# --------------------------------------------------------------------

from newscoop import config_service

# --------------------------------------------------------------------

from ally import config_web, web

if __name__ == '__main__':
    config_web.location = 'localhost'
    config_web.port = 80
    config_web.serviceConfigModule = config_service
    config_web.setup()
    web.run()
