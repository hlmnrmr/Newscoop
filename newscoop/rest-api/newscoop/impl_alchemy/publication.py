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
from newscoop.impl_alchemy.meta import publication as pm
from sqlalchemy.orm.exc import NoResultFound
import logging
from newscoop.impl_alchemy import SessionSupport

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class PublicationServiceAlchemy(IPublicationService, SessionSupport):
    '''
    Test implementation for @see: IPublicationService
    '''
    
    def __init__(self):
        super().__init__(self)
        SessionSupport.__init__(self)

    def byId(self, id):
        try:
            return self.session().query(Publication).filter(pm.Id == id).one()
        except NoResultFound:
            raise InputException(_('No publication for id ($1)', id))

    def all(self, offset=None, limit=None, q=None):
        aq = self.session().query(pm.Id)
        if q is not None:
            assert isinstance(q, QPublication)
            if q.name.like is not None:
                aq = aq.filter(pm.Name.like(q.name.like))
            if q.name.orderAscending is not None:
                if q.name.orderAscending:
                    aq = aq.order_by(pm.Name)
                else:
                    aq = aq.order_by(pm.Name.desc())
        if offset is not None: aq = aq.offset(offset)
        if limit is not None: aq = aq.limit(limit)
        ids = (tup[0] for tup in aq.all())
        return ids

    # ---------------------------------------------
 
    def insert(self, entity):
        raise NotImplemented

    def update(self, entity):
        raise NotImplemented

    def delete(self, id):
        return self.session().query(Publication).filter(pm.Id == id).delete() > 0
