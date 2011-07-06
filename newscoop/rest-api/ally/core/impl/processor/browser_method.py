'''
Created on Jul 5, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the support for understanding the method provided by the browser as a parameter.
'''

import logging
from ally.core.util import injected
from ally.core.spec.server import Processor

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class BrowserMethodHandler(Processor):
    '''
    Implementation for a processor that provides support for methods transmitted as parameters by browsers.
    '''

    def process(self, request, response, chain):
        '''
        @see: Processor.process
        '''
        raise NotImplemented('Needs to be implemented latter on, no time right now.')
