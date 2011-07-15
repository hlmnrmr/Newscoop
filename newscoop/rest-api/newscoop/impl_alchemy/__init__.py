'''
Created on Jun 23, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for the generic entities API.
'''

from ally.core.api.configure import ServiceSupport
from ally.core.api.criteria import AsLike, AsOrdered
from ally.core.api.exception import InputException
from ally.core.api.operator import Model, Property, Query, CriteriaEntry
from ally.core.internationalization import msg as _
from ally.core.support.sql_alchemy import SessionSupport, ENGINE_NAME, \
    PropertySepcificationAlchemy
from newscoop.api import IEntityCRUDService, Entity, IEntityFindService, \
    IEntityQueryService, IEntityService
from sqlalchemy.orm.exc import NoResultFound

# --------------------------------------------------------------------

class EntitySupportAlchemy(SessionSupport):
    '''
    Provides support generic entity handling.
    '''
    
    model = Model
    
    def __init__(self, model):
        assert isinstance(model, Model), 'Invalid model %s' % model
        super().__init__()
        self.model = model
        if isinstance(self, ServiceSupport):
            ServiceSupport.__init__(self, self)

# --------------------------------------------------------------------

class EntityFindServiceAlchemy(EntitySupportAlchemy):
    '''
    Generic implementation for @see: IEntityFindService
    '''
    
    model = Model
    
    def __init__(self, model):
        super().__init__(model)
    
    def byId(self, id):
        '''
        @see: IEntityFindService.byId
        '''
        try:
            return self.session().query(self.model.modelClass).\
                filter(self.getColumnProperty('Id') == id).one()
        except NoResultFound:
            raise InputException(_('No $1 for id ($2)', self.model.name, id))
    
    def getColumnProperty(self, propertyName):
        '''
        Provides the alchemy column for the specified property name.
        '''
        assert isinstance(propertyName, str) and propertyName != '', \
        'Invalid property name %s' % propertyName
        prop = self.model.properties.get(propertyName, None)
        assert isinstance(prop, Property), 'Maybe the %s attribute name has changed?' % propertyName
        spec = prop.sepcificationFor(ENGINE_NAME)
        assert isinstance(spec, PropertySepcificationAlchemy), \
        'Maybe you should use the mapperModel from SQL alchemy support?'
        return spec.coulmn

# --------------------------------------------------------------------

class EntityCRUDServiceAlchemy(EntitySupportAlchemy):
    '''
    Generic implementation for @see: IEntityCRUDService
    '''
    
    model = Model
    
    def __init__(self, model):
        super().__init__(model)

    def insert(self, entity):
        '''
        @see: IEntityCRUDService.insert
        '''
        assert isinstance(entity, self.model.modelClass), \
        'Invalid entity %s, expected class %s' % (entity, self.model.modelClass)
        self.session().add(entity)
        self.session().flush((entity,))
        return entity.Id

    def update(self, entity):
        '''
        @see: IEntityCRUDService.update
        '''
        assert isinstance(entity, self.model.modelClass), \
        'Invalid entity %s, expected class %s' % (entity, self.model.modelClass)
        self.session().merge(entity)
        return True

    def delete(self, id):
        '''
        @see: IEntityCRUDService.delete
        '''
        return self.session().query(self.model.modelClass).\
            filter(self.getColumnProperty('Id') == id).delete() > 0

# --------------------------------------------------------------------

class EntityQueryServiceAlchemy(EntityFindServiceAlchemy):
    '''
    Generic implementation for @see: IEntityQueryService
    '''
    
    model = Model
     
    def __init__(self, model):
        assert model.query is not None, 'Invalid model %s has no query' % model
        super().__init__(model)
        
    def all(self, offset=None, limit=None, q=None):
        '''
        @see: IEntityQueryService.all
        '''
        aq = self.session().query(self.getColumnProperty('Id'))
        if q is not None:
            aq = self.buildQuery(aq, q)
        if offset is not None: aq = aq.offset(offset)
        if limit is not None: aq = aq.limit(limit)
        # SQL alchemy returns the id in a tuple
        ids = (tup[0] for tup in aq.all())
        return ids
    
    def buildQuery(self, aq, query):
        assert isinstance(query, self.model.query.queryClass), \
        'Invalid query %s, expected class %s' % (query, self.model.query.queryClass)
        for crtEnt in self.model.query.criteriaEntries.values():
            assert isinstance(crtEnt, CriteriaEntry)
            crt = crtEnt.get(query)
            if crt is not None:
                if isinstance(crt, AsLike):
                    assert isinstance(crt, AsLike)
                    if crt.like is not None:
                        aq = aq.filter(self.getColumnCriteria(crtEnt.name).like(crt.like))
                if isinstance(crt, AsOrdered):
                    assert isinstance(crt, AsOrdered)
                    if crt.orderAscending is not None:
                        if crt.orderAscending:
                            aq = aq.order_by(self.getColumnCriteria(crtEnt.name))
                        else:
                            aq = aq.order_by(self.getColumnCriteria(crtEnt.name).desc())
        return aq
                            
    def getColumnCriteria(self, criteriaName):
        '''
        Provides the alchemy column for the specified criteria name.
        '''
        assert isinstance(criteriaName, str) and criteriaName != '', \
        'Invalid criteria name %s' % criteriaName
        criteriaName = criteriaName.lower()
        for name in self.model.properties:
            if name.lower() == criteriaName:
                break
        else:
            raise AssertionError('Could not locate any property name for criteria name %s' % criteriaName)
        prop = self.model.properties[name]
        spec = prop.sepcificationFor(ENGINE_NAME)
        assert isinstance(spec, PropertySepcificationAlchemy), \
        'Maybe you should use the mapperModel from SQL alchemy support?'
        return spec.coulmn

# --------------------------------------------------------------------

class EntityServiceAlchemy(EntityQueryServiceAlchemy, EntityCRUDServiceAlchemy):
    '''
    Generic implementation for @see: IEntityQueryService
    '''
    
    def __init__(self, model):
        super().__init__(model)
    
# --------------------------------------------------------------------




# --------------------------------------------------------------------
