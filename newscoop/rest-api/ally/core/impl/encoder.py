'''
Created on Jun 17, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides encoders implementations.
'''

from xml.sax.saxutils import escape
from ally.core.spec.presenting import Encoder, EncoderFactory
from ally.core.spec.resources import Path, Converter
from ally.core.util import injected
from ally.core.spec.server import Response

# --------------------------------------------------------------------

class EncoderBase(Encoder):
    '''
    Provides the base class for the encoders.
    Attention this class needs to be extended to provide the actual functionality.
    '''
    
    def __init__(self, out, response, factory):
        '''
        Initialize the encoder.
        
        @param out: object
            A writer object that has a 'write' method, used for outputting the content.
        @param encoderPath: EncoderPath
            The path encoder to be used by this content encoder when writing request paths.
        @param factory: EncoderBaseFactory
            The factory that created this encoder.
        '''
        assert getattr(out, 'write', None) is not None, 'Invalid output provided %s, has no write method' % out
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(factory, EncoderFactory), 'Invalid factory %s' % factory
        def output(content):
            out.write(bytes(content, response.charSet))
        self._out = output
        self._response = response
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
    
# --------------------------------------------------------------------

class EncoderXMLIndented(EncoderBase):
    '''
    Provides encoding in XML form that also has proper indentation.
    '''

    def __init__(self, out, response, factory):
        '''
        @see: EncoderBase.__init__
        '''
        assert isinstance(factory, EncoderXMLFactory), 'Invalid XML encoder factory %s' % factory
        super().__init__(out, response, factory)
        self._indent = ''
    
    def put(self, name, value=None, type=None, path=None):
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
            self._out(escape(self._response.encoderPath.encode(path)))
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
            self._out('<?xml version="1.0" encoding="')
            self._out(self._response.charSet)
            self._out('"?>')
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

@injected
class EncoderXMLFactory(EncoderFactory):
    '''
    Provides the XML encoders factory.
    '''
    
    converter = Converter
    # The converter used by the encoders of this factory.
    indented = '    '
    # The indented block to use default 4 spaces, can be changed.
    lineEnd = '\n'
    # The line end to use by default \n, can be changed.
    
    def __init__(self):
        assert isinstance(self.converter, Converter), 'Invalid Converter object %s' % self.converter
        assert isinstance(self.indented, str), 'Invalid string %s' % self.indented
        assert isinstance(self.lineEnd, str), 'Invalid string %s' % self.lineEnd
 
    def createEncoder(self, rsp, out):
        '''
        @see: EncoderFactory.createEncoder
        '''
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        return EncoderXMLIndented(out, rsp, self)
        
# --------------------------------------------------------------------
