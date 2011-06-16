'''
Created on Jun 8, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

API specifications for themes.
'''

from newscoop.api.entity import Entity
from newscoop.core.api.decorator import APIProperty as prop, APIModel as model
from newscoop.core.api.type import String

@model()
class Theme(Entity):
    '''
    Provides the publication model.
    '''
        
    # ----------------------------------------------------------------
    
    @prop(String)
    def name(self):
        '''
        '''
    
    @prop(String)
    def designer(self):
        '''
        '''
    
    @prop(String)
    def version(self):
        '''
        '''
        
    @prop(String)
    def minorNewscoopVersion(self):
        '''
        '''
    
    @prop(String)
    def description(self):
        '''
        '''
    
# --------------------------------------------------------------------

class IThemeService:
    '''
    '''
    
    # ----------------------------------------------------------------
    
    def getThemes(self, orderBy=None, offset=0, limit= -1, publicationId=None, name=None, designer=None, version=None,
                 minorNewscoopVersion=None, description=None):
        '''
        use composition with a base implementation
        '''
        
    def getUnassignedThemes(self, orderBy=None, offset=0, limit= -1, name=None, designer=None, version=None,
                 minorNewscoopVersion=None, description=None):
        '''
        '''

    def getPresentationImages(self, id):
        '''
        '''

    def putTheme(self):
        '''
        The xml will look like 
        <theme>
            <id>1212</id>
            <name></name>
        </theme>
        '''
        pass

# --------------------------------------------------------------------

