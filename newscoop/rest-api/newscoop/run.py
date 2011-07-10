'''
Created on Jul 6, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Used for starting the web server.
'''

# --------------------------------------------------------------------

import logging
from ally.core import util
util.GUARD_ENABLED = __debug__
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARN)
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.WARNING)

# --------------------------------------------------------------------

from newscoop import service_config
from ally.http import server_config, server
from sqlalchemy.engine import create_engine
from newscoop.impl_alchemy.meta import meta

# --------------------------------------------------------------------

if __name__ == '__main__':
    engine = create_engine("sqlite:///newscoop.db", encoding='utf8', echo=__debug__)
    meta.create_all(engine)

    server_config.serverLocation = 'localhost'
    server_config.serverPort = 80
    service_config.engine = engine
    service_config.setupAll()
    
    server.run()
