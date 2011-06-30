'''
Created on Jun 23, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Test implementation for publication API.
'''

from newscoop.api.publication import IPublicationService, Publication

# --------------------------------------------------------------------

class PublicationServiceTest(IPublicationService):
    '''
    Test implementation for @see: IPublicationService
    '''
    
    def __init__(self):
        self.publications = {}
        for i in range(1, 100):
            pub = Publication()
            pub.id = i
            pub.name = 'Publication ' + str(i)
            self.publications[i] = pub

    def byId(self, id):
        return self.publications[id]

    def all(self, q=None):
        return self.publications.keys()

    # ---------------------------------------------
 
    def insert(self, entity):
        raise NotImplemented

    def update(self, entity):
        raise NotImplemented

    def delete(self, id):
        raise NotImplemented
