'''
Created on Jul 2, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides dummy data for services based on the APIs.
'''
from ally.core.api.configure import serviceFor
from ally.core.api.operator import Service, Model, Property
from ally.core.api.type import Boolean, Integer, Number, String, Id
from ally.core.spec.resources import ResourcesManager
from ally.core.util import classForName, injected
from inspect import isclass
import random

# --------------------------------------------------------------------

@injected
class ServiceDummy:
    '''
    Class providing dummy data for service APIs.
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the additional resources required.
    entitiesCount = 30
    # The number of dummy entities to create.
    
    def __init__(self, serviceClass):
        '''
        Constructs the dummy service for the provided service class.
        
        @param serviceClass: class|string
            The service class or fully qualified name of the service class.
        '''
        if isinstance(serviceClass, str):
            self.clazz = classForName(serviceClass)
            assert isclass(self.clazz), 'Cannot find a class for name %s' % serviceClass
        else:
            assert isclass(serviceClass), 'Invalid class %s, you can also specify the full name' % serviceClass 
            self.clazz = serviceClass
        self.service = serviceFor(self.clazz)
        assert isinstance(self.service, Service), 'Invalid class %s, could not locate the service' % self.clazz
        serviceFor(self, self.service)

    def _populate(self):
        '''
        FOR INTERNAL USE ONLY.
        Populates dummy data into this dummy service.
        '''
        model = self.service.model
        assert isinstance(model, Model)
        self.objects = [model.modelClass() in range(0, self.entitiesCount)]
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            if prop.type == Boolean.api_type:
                for obj in self.objects:
                    prop.set(obj, random.choice((True, False)))
            if prop.type == Integer.api_type or prop.type == Id.api_type:
                for k, obj in enumerate(self.objects):
                    prop.set(obj, k)
            if prop.type == Number.api_type:
                for obj in self.objects:
                    prop.set(obj, random.random())
            if prop.type == String.api_type:
                for k, obj in enumerate(self.objects):
                    prop.set(obj, prop.name + ' for ' + (k + 1))
    
    def __getattr__(self, name):
        pass