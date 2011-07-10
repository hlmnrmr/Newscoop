'''
Created on Jul 6, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy service implementations.
'''

from ally.core.spec.server import Processor, ProcessorsChain, Response
from ally.core.util import injected
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.session import Session, sessionmaker
from threading import current_thread
import logging
import traceback

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
class AlchemySessionHandler(Processor):
    '''
    Implementation for a processor that provides the SQLAlchemy session handling.
    '''
    
    engine = Engine
    
    def __init__(self):
        '''
        Construct the session stuff.
        '''
        assert isinstance(self.engine, Engine), 'Invalid engine %s' % self.engine
        self.session = sessionmaker(bind=self.engine)

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        setattr(current_thread(), NAME_SQL_SESSION, self.session())
        log.debug('Created SQL Alchemy session')
        try:
            chain.process(req, rsp)
        except:
            self._rollback()
            raise
        if rsp.code.isSuccess:
            self._commit()
        else:
            self._rollback()

    def _commit(self):
        '''
        Commit the current thread session.
        '''
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

    def _rollback(self):
        '''
        Roll back the current thread session.
        '''
        thread = current_thread()
        session = getattr(thread, NAME_SQL_SESSION, None)
        if session is not None:
            session.rollback()
            session.close()
            delattr(thread, NAME_SQL_SESSION)
            log.warning('Improper SQL Alchemy session, rolled back transactions')
