'''
Created on Jul 6, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy service implementations.
'''

from ally.core.spec.server import Processor, ProcessorsChain
from ally.core.util import injected
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session, sessionmaker
from threading import current_thread
import logging
import traceback
from sqlalchemy.exc import InvalidRequestError

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

NAME_SQL_SESSION = '__sql_session__'

# --------------------------------------------------------------------

class SessionSupport:
    '''
    Class that provides for the services that use SQLAlchemy the session support.
    '''
    
    session = Session
    
    def __init__(self):
        '''
        Bind the session method.
        '''
        self.session = _getSession

def _getSession():
    '''
    Function to provide the session on the current thread.
    '''
    session = getattr(current_thread(), NAME_SQL_SESSION, None)
    assert session is not None, 'Invalid call, it seems that the thread is not tagged with an SQL session'
    return session

# --------------------------------------------------------------------

@injected
class AlchemyOpenSessionHandler(Processor):
    '''
    Implementation for a processor that provides the SQLAlchemy session handling.
    '''
    
    engine = Engine
    
    def __init__(self):
        '''
        Construct the session stuff.
        '''
        self.session = sessionmaker(bind=self.engine)
        

    def process(self, request, response, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        setattr(current_thread(), NAME_SQL_SESSION, self.session())
        log.debug('Created SQL Alchemy session')
        try:
            chain.process(request, response)
        finally:
            # If the thread still has a session after the chain completion it means that something went wrong
            # since the AlchemyCloseSessionHandler should have disposed of this session.
            thread = current_thread()
            session = getattr(thread, NAME_SQL_SESSION, None)
            if session is not None:
                session.rollback()
                session.close()
                delattr(thread, NAME_SQL_SESSION)
                log.debug('Improper SQL Alchemy session, rolled back transactions')

class AlchemyCloseSessionHandler(Processor):
    '''
    Implementation for a processor that closes the SQLAlchemy session.
    '''

    def process(self, request, response, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        # If the thread has a session it means that we need to commit it and close it.
        thread = current_thread()
        session = getattr(thread, NAME_SQL_SESSION, None)
        if session is not None:
            assert isinstance(session, Session)
            try:
                session.commit()
                log.debug('Committed SQL Alchemy session transactions')
            except InvalidRequestError:
                log.debug('Nothing to commit on SQL Alchemy session')
            session.close()
            delattr(thread, NAME_SQL_SESSION)
            log.debug('Properly closed SQL Alchemy session')
        chain.process(request, response)
