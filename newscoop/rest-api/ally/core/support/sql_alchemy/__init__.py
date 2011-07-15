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
from inspect import isclass
from sqlalchemy.schema import Table, Column
from ally.core.api.configure import propertiesFor
from ally.core.api.operator import Model, PROPERTY_PREFIX, Property, \
    PropertySepcification
from sqlalchemy.orm import mapper
from sqlalchemy.types import String

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

NAME_SQL_SESSION = '__sql_session__'
ENGINE_NAME = 'alchemy'

# --------------------------------------------------------------------

def mapperModel(modelClass, sqlTable):
    '''
    Maps a table to a ally REST model. Use this instead of the classical SQL alchemy mapper since this will
    also provide to the model additional information extracted from the SQL alchemy configurations.
    
    @param modelClass: class
        The model class to be mapped with the provided sql table.
    @param sqlTable: Table
        The table to map the model with.
    '''
    assert isclass(modelClass), 'Invalid model class %s' % modelClass
    assert isinstance(sqlTable, Table), 'Invalid SQL alchemy table %s' % sqlTable
    model = propertiesFor(modelClass)
    assert isinstance(model, Model), 'Invalid class %s is not a model' % modelClass
    for column in sqlTable.columns:
        assert isinstance(column, Column)
        if column.key is not None:
            prop = model.properties.get(column.key, None)
            if prop is not None:
                assert isinstance(prop, Property)
                #TODO: add checking if the column type is the same with the property
                prop.sepcificationFor(ENGINE_NAME, PropertySepcificationAlchemy(prop, column))
    mapper(modelClass, sqlTable, column_prefix=PROPERTY_PREFIX)

class PropertySepcificationAlchemy(PropertySepcification):
    '''
    Specification extension for SQL alchemy.
    '''
    
    def __init__(self, property, column):
        assert isinstance(property, Property), 'Invalid property %s' % property
        assert isinstance(column, Column), 'Invalid column %s' % column
        length = None
        typ = column.type
        if isinstance(typ, String):
            assert isinstance(typ, String)
            length = typ.length
        super().__init__(property, column.nullable == False, length)
        self.coulmn = column

# --------------------------------------------------------------------

class SessionSupport:
    '''
    Class that provides for the services that use SQLAlchemy the session support.
    All services that use SQLAlchemy have to extend this class in order to provide the sql alchemy session
    of the request, the session will be automatically handled by the session processor.
    '''
    
    session = Session
    
    def __init__(self):
        '''
        Bind the session method.
        '''
        self.session = _getSession

# --------------------------------------------------------------------

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
