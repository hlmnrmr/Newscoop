'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for issue API.
'''

from newscoop.impl_alchemy.meta import meta
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer, String

# --------------------------------------------------------------------

Id = Column('id', Integer, primary_key=True, key='Id')
Name = Column('name', String(100), nullable=False, key='Name')
Number = Column('number', String(100), nullable=False, key='Number')
Description = Column('description', String(200), nullable=True, key='Description')

publication = Column('publication_id', ForeignKey('publication.Id'), nullable=True)

table = Table('issue', meta, Id, Name, Number, Description, publication, mysql_engine='InnoDB')
