'''
Created on Jun 17, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides encoders implementations.
'''

from _abcoll import Callable
from xml.sax.saxutils import escape
from ally.core.spec.presenting import Encoder, EncoderPath, EncoderFactory
from ally.core.spec.resources import Path, Converter
from ally.core.spec import content_type
from ally.core.util import injected

# --------------------------------------------------------------------

class EncoderBase(Encoder):
    '''
    Provides the base class for the encoders.
    Attention this class needs to be extended to provide the actual functionality.
    '''
    
    def __init__(self, out, encoderPath, factory):
        '''
        Initialize the encoder.
        
        @param out: Callable
            The output Callable used for writing content.
        @param encoderPath: EncoderPath
            The path encoder to be used by this content encoder when writing request paths.
        @param factory: EncoderBaseFactory
            The factory that created this encoder.
        '''
        assert isinstance(out, Callable), 'Invalid output Callable provided %s' % out
        assert isinstance(encoderPath, EncoderPath), 'Invalid encoder path %s' % encoderPath
        assert isinstance(factory, EncoderBaseFactory), 'Invalid factory %s' % factory
        self._out = out
        self._encoderPath = encoderPath
        self._factory = factory
        self.__nameStack = []
        self.__opened = True
    
    def isEmpty(self):
        '''
        Checks if the current encoder is empty, meaning that no block has been opened.
        
        @return: boolean
            True if the encoder is empty, false otherwise.
        '''
        return self.__opened and len(self.__nameStack) == 0
    
    def put(self, name, value, path=None):
        '''
        @see: Encoder.put
        '''
        assert isinstance(name, str), 'The name %s needs to be a string' % name
        assert path is None or isinstance(path, Path), 'Invalid path %s, can be None' % path
        assert self.__opened, 'The encoder is closed'
        assert not self.isEmpty(), 'You need to first open a root block'
    
    def open(self, name):
        '''
        @see: Encoder.open
        '''
        assert isinstance(name, str), 'The name %s needs to be a string' % name
        assert self.__opened, 'The encoder is closed'
        self.__nameStack.append(name)
    
    def close(self):
        '''
        @see: Encoder.close
        '''
        assert self.__opened, 'The encoder is closed'
        name = self.__nameStack.pop()
        if len(self.__nameStack) == 0:
            self.__opened = False
        return name

@injected
class EncoderBaseFactory(EncoderFactory):
    '''
    Provides the base encoders factory class.
    Attention this class needs to be extended to provide the actual functionality.
    '''
    
    converter = Converter
    # The converter used by the encoders of this factory.
    
    def __init__(self, contentType):
        '''
        @see: EncoderFactory.__init__
        '''
        super().__init__(contentType)

    def isValidFormat(self, format):
        '''
        @see: EncoderFactory.isValidFormat
        '''
        assert isinstance(format, str), 'Invalid format %s' % format
        return self.contentType.format == format.lower()
    
# --------------------------------------------------------------------

class EncoderXMLIndented(EncoderBase):
    '''
    Provides encoding in XML form that also has proper indentation.
    '''

    def __init__(self, out, encoderPath, factory):
        '''
        @see: EncoderBase.__init__
        '''
        super().__init__(out, encoderPath, factory)
        self._indent = ''
    
    def put(self, name, value=None, path=None):
        '''
        @see: Encoder.put
        '''
        fact = self._factory
        assert isinstance(fact, EncoderXMLFactory)
        name = fact.converter.normalize(name)
        super().put(name, value, path)
        self._out(self._indent)
        self._out('<')
        self._out(name)
        if path is not None:
            self._out(' href="')
            self._out(escape(self._encoderPath.encode(path)))
            self._out('"')
        if value is not None:
            self._out('>')
            self._out(escape(fact.converter.asString(value)))
            self._out('</')
            self._out(name)
            self._out('>')
        else:
            self._out('/>')
        self._out(fact.lineEnd)
        
    def open(self, name):
        '''
        @see: Encoder.open
        '''
        fact = self._factory
        assert isinstance(fact, EncoderXMLFactory)
        if self.isEmpty():
            self._out('<?xml version="1.0" encoding="utf-8"?>')
            self._out(fact.lineEnd)
        name = fact.converter.normalize(name)
        super().open(name)
        self._out(self._indent)
        self._out('<')
        self._out(name)
        self._out('>')
        self._out(fact.lineEnd)
        self._indent += fact.indented
        
    def close(self):
        '''
        @see: Encoder.close
        '''
        fact = self._factory
        assert isinstance(fact, EncoderXMLFactory)
        name = super().close()
        self._indent = self._indent[:-len(fact.indented)]
        self._out(self._indent)
        self._out('</')
        self._out(name)
        self._out('>')
        self._out(fact.lineEnd)
        return name
    
    def __str__(self):
        return self.__class__.__name__

class EncoderXMLFactory(EncoderBaseFactory):
    '''
    Provides the XML encoders factory.
    '''
    
    indented = '    '
    # The indented block to use default 4 spaces, can be changed.
    lineEnd = '\n'
    # The line end to use by default \n, can be changed.
    
    def __init__(self):
        '''
        @see: EncoderFactory.__init__
        '''
        super().__init__(content_type.XML)

    def createEncoder(self, encoderPath, out):
        '''
        @see: EncoderFactory.createEncoder
        '''
        return EncoderXMLIndented(out, encoderPath, self)
        
# --------------------------------------------------------------------
