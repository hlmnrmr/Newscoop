'''
Created on Jul 6, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

This module contains all the table definitions that are required by alchemy services implementations.
'''

from sqlalchemy.schema import MetaData

# --------------------------------------------------------------------

meta = MetaData()
# Provides the meta object for SQL alchemy.