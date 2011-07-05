'''
Created on Jun 23, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Test implementation for publication API.
'''

from newscoop.api.publication import IPublicationService, Publication, \
    QPublication

# --------------------------------------------------------------------

class PublicationServiceTest(IPublicationService):
    '''
    Test implementation for @see: IPublicationService
    '''
    
    def __init__(self):
        super().__init__(self)
        self.publications = {}
        for i in range(1, 1000):
            pub = Publication()
            pub.Id = i
            pub.Name = 'Publication ' + str(i)
            self.publications[i] = pub

    def byId(self, id):
        return self.publications[id]

    def all(self, offset=None, limit=None, q=None):
        k = 0
        for id, pub in self.publications.items():
            assert isinstance(pub, Publication)
            if (offset is None or k >= offset) and (limit is None or k - offset < limit):
                if q is not None:
                    assert isinstance(q, QPublication)
                    if q.name.like is not None:
                        if pub.Name.find(q.name.like) >= 0:
                            yield id
                    else:
                        yield id
                else:
                    yield id
            k += 1

    # ---------------------------------------------
 
    def insert(self, entity):
        raise NotImplemented

    def update(self, entity):
        raise NotImplemented

    def delete(self, id):
        raise NotImplemented
