'''
Created on Jun 23, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Test implementation for publication API.
'''

from newscoop.api.publication import IPublicationService, Publication

# --------------------------------------------------------------------

class PublicationServiceTest(IPublicationService):
    '''
    Test implementation for @see: IPublicationService
    '''
    
    def __init__(self):
        super().__init__(self)
        self.publications = {}
        for i in range(1, 10):
            pub = Publication()
            pub.Id = i
            pub.Name = 'Publication ' + str(i)
            self.publications[i] = pub

    def byId(self, id):
        return self.publications[id]

    def all(self, offset=None, limit=None, q=None):
        k = 0
        for id in self.publications.keys():
            if (offset is None or k >= offset) and (limit is None or k - offset < limit):
                yield id
            k += 1

    # ---------------------------------------------
 
    def insert(self, entity):
        raise NotImplemented

    def update(self, entity):
        raise NotImplemented

    def delete(self, id):
        raise NotImplemented
