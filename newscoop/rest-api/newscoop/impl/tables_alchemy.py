'''
Created on Jul 6, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the tables for SQL alchemy.
'''

from newscoop.api.publication import Publication
from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine
from sqlalchemy.orm import mapper
from ally.core.api.operator import PROPERTY_PREFIX

# --------------------------------------------------------------------

meta = MetaData()

tablePublication = Table('publication', meta,
    Column('id', Integer, primary_key=True, key='Id'),
    Column('name', String(100), nullable=False, key='Name'),
    mysql_engine='InnoDB')

mapper(Publication, tablePublication, column_prefix=PROPERTY_PREFIX)

# --------------------------------------------------------------------

db = create_engine("sqlite:///newscoop.db", encoding='utf8', echo=True)
meta.create_all(db)
