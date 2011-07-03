'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing specifications for the presenting of resources.
'''

from ally.core.api.type import Type
from ally.core.spec.content_type import ContentType
from ally.core.util import guard, injected
import abc

# --------------------------------------------------------------------

@guard
class EncoderPath(metaclass=abc.ABCMeta):
    '''
    Provides the path encoding.
    '''
    
    @abc.abstractmethod
    def encode(self, path):
        '''
        Encodes the provided path to a full request path.
        
        @param path: Path
            The path to be encoded.
        @return: object
            The full compiled request path, the type depends on the implementation.
        '''

@guard
class Encoder(metaclass=abc.ABCMeta):
    '''
    Provides the base class for the encoders.
    '''
    
    @abc.abstractmethod
    def open(self, name):
        '''
        Opens a new containing block of sub elements.
        Attention each block opened needs to be closed, and all succeeding elements belong to the currently
        open block.
        
        @param name: string
            The name of the block.
        '''
    
    @abc.abstractmethod
    def put(self, name, value=None, path=None):
        '''
        Encode the name value pair.
        
        @param name: string
            The name of the element.
        @param value: object
            The element value to encode, the type is mostly depended on the encoder implementation.
        @param path: Path
            A path linking the element.
        '''
    
    @abc.abstractmethod
    def close(self):
        '''
        Close the currently opened block.
        
        @return: string
            The name of the closed block.
        '''

@guard
class EncoderFactory(metaclass=abc.ABCMeta):
    '''
    Factory for providing encoders.
    '''
    
    def __init__(self, contentType):
        '''
        Constructs the encoder path.
        
        @param contentType: ContentType
            The content type of the encoder factory.
        '''
        assert isinstance(contentType, ContentType), 'Invalid content type %s' % contentType
        self.contentType = contentType
    
    @abc.abstractmethod
    def isValidFormat(self, format):
        '''
        Checks if the provided format is valid for this encoder factory.
        
        @param format: object
            The format desired.
        '''
    
    @abc.abstractmethod
    def createEncoder(self, encoderPath, out):
        '''
        Creates an encoder specific for this path encoder for the provided output.
        
        @param encoderPath: EncoderPath
            The path encoder that will be used by the encoder to code the paths.
        @param out: Callable
            The output Callable used for writing content.
        @return: Encoder
            The new encoder.
        '''

# --------------------------------------------------------------------

class Render(metaclass=abc.ABCMeta):
    '''
    Class that handles the rendering of model objects to encoders.
    '''
    
    @abc.abstractmethod
    def render(self, obj, objType, encoder, renders):
        '''
        Render in the encoder the provided object based on the provided object type.
        
        @param obj: object
            The object to be rendered 
        @param objType: Type
            The type of the object to encode.
        @param encoder: Encoder
            The encoder to write to object to.
        @param renders: Renders
            The renders to use in encoding sub components of the object.
        @return: boolean
            Returns True if the render has been successful for the object, false if this render cannot perform for
            the provided object type.
        '''

@injected
@guard
class Renders:
    '''
    A simple container of renders.
    '''
    
    renders = list
    # The list of render objects.
    
    def __init__(self):
        if __debug__:
            for render in self.renders:
                assert isinstance(render, Render), 'Invalid renderer %s' % render
    
    def render(self, obj, objType, encoder):
        '''
        Render fully in the encoder the provided object based on the provided object type.
        
        @param obj: object
            The object to be rendered 
        @param objType: Type
            The type of the object to encode.
        @param encoder: Encoder
            The encoder to write to object to.
        '''
        assert isinstance(objType, Type), 'Invalid object type %s' % objType
        assert isinstance(encoder, Encoder), 'Invalid encoder %s' % encoder
        for render in self.renders:
            assert isinstance(render, Render)
            if render.render(obj, objType, encoder, self):
                break
