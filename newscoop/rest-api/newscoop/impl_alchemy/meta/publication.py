'''
Created on Jul 7, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for publication API.
'''

from ally.core.api.operator import PROPERTY_PREFIX
from newscoop.api.publication import Publication
from newscoop.impl_alchemy.meta import meta
from sqlalchemy.orm import mapper
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import Integer, String

# --------------------------------------------------------------------

Id = Column('id', Integer, primary_key=True, key='Id')
Name = Column('name', String(100), nullable=False, key='Name')

table = Table('publication', meta, Id, Name, mysql_engine='InnoDB')
mapper(Publication, table, column_prefix=PROPERTY_PREFIX)
