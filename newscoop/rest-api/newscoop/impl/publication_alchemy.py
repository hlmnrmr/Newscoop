'''
Created on Jun 23, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for publication API.
'''

from ally.core.api.exception import InputException
from ally.core.internationalization import msg as _
from ally.core.util import injected
from newscoop.api.publication import IPublicationService, Publication, \
    QPublication
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import Table
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class PublicationServiceAlchemy(IPublicationService):
    '''
    Test implementation for @see: IPublicationService
    '''
    
    db = Engine
    table = Table
    
    def __init__(self):
        pub = Publication()
        pub.Name = 'Publication 1'
        sess = Session(self.db)
        sess.add(pub)
        pub = Publication()
        pub.Name = 'Publication 2'
        sess.add(pub)
        sess.commit()
        pass

    def byId(self, id):
        sess = Session(self.db)
        try:
            return sess.query(Publication).filter(self.table.c.Id == id).one()
        except Exception:
            raise InputException(_('No publication for id ($1)', id))

    def all(self, offset=None, limit=None, q=None):
        sess = Session(self.db)
        aq = sess.query(self.table.c.Id)
        if q is not None:
            assert isinstance(q, QPublication)
            if q.name.like is not None:
                aq = aq.filter(self.table.c.Name.like(q.name.like))
            if q.name.orderAscending is not None:
                if q.name.orderAscending:
                    aq = aq.order_by(self.table.c.Name)
                else:
                    aq = aq.order_by(self.table.c.Name.desc())
        if offset is not None: aq = aq.offset(offset)
        if limit is not None: aq = aq.limit(limit)
        return (tup[0] for tup in aq.all())

    # ---------------------------------------------
 
    def insert(self, entity):
        raise NotImplemented

    def update(self, entity):
        raise NotImplemented

    def delete(self, id):
        raise NotImplemented
