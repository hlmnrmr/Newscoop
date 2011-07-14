'''
Created on Jul 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoders/decoders for the HTTP header.
'''

from ally.core.internationalization import msg as _
from ally.core.spec.server import Response, GET, DELETE, INSERT, UPDATE
from ally.core.util import injected, findInValues
from ally.http.spec import DecoderHeader, EncoderHeader, HeaderException, \
    ParserHeader, RequestHTTP
import re
from ally.core.spec.resources import ResourcesManager

# --------------------------------------------------------------------

@injected
class EncPsrContentType(EncoderHeader, ParserHeader):
    '''
    Implementation for the header encoder/parser for content type.
    @see: EncoderHeader, ParserHeader
    '''
    
    contentTypes = dict
    # The content types map.
    charSets = dict
    # The character set map.
    name = 'Content-Type'
    sepParam = ';'
    sepAttrValue = '='
    attrCharSet = 'charset'
    reCharSet = re.compile('[\s]*charset[\s]*=[\s]*(?P<charset>.+)[\s]*')
    
    def __init__(self):
        assert isinstance(self.contentTypes, dict), 'Invalid content types dictionary %s' % self.contentTypes
        assert isinstance(self.charSets, dict), 'Invalid char sets dictionary %s' % self.charSets
        assert isinstance(self.name, str), 'Invalid string %s' % self.name
        assert isinstance(self.sepParam, str), 'Invalid string %s' % self.sepParam
        assert isinstance(self.sepAttrValue, str), 'Invalid string %s' % self.sepAttrValue
        assert isinstance(self.attrCharSet, str), 'Invalid string %s' % self.attrCharSet
        assert self.reCharSet is not None, 'Invalid pattern %s' % self.reCharSet
    
    def encode(self, headers, rsp):
        '''
        @see: EncoderHeader.encode
        '''
        assert isinstance(headers, dict), 'Invalid headers dictionary %s' % headers
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        if rsp.contentType is not None:
            vals = self.contentTypes[rsp.contentType]
            vals = [vals[0] if isinstance(vals, list) else vals]
            if rsp.charSet is not None:
                vals.extend([self.sepParam, self.attrCharSet, self.sepAttrValue, rsp.charSet])
            headers[self.name] = ''.join(vals)
    
    def parse(self, headers):
        '''
        @see: ParserHeader.parse
        
        @return: tuple(content type, character set|None)
            Provides a tuple containing the content type (string) and character set (string).
        '''
        assert isinstance(headers, dict), 'Invalid headers dictionary %s' % headers
        if self.name not in headers:
            raise HeaderException(_('No ($1) available', self.name))
        vals = headers[self.name].split(self.sepParam)
        val = vals[0].lower()
        contentType = findInValues(self.contentTypes, val)
        if contentType is None: raise HeaderException(_('Unknown content type ($1)', val))
        charSet = None
        if len(vals) > 1:
            for k in range(1, len(vals)):
                m = self.reCharSet.match(vals[k])
                if m is not None:
                    charSet = findInValues(self.charSets, m.group('charset'))
                    break
        return (contentType, charSet)
    
# --------------------------------------------------------------------

@injected
class ParserContentLength(ParserHeader):
    '''
    Implementation for the header parser for content length.
    @see: ParserHeader
    '''
    
    name = 'Content-Length'
    
    def __init__(self):
        assert isinstance(self.name, str), 'Invalid string %s' % self.name
    
    def parse(self, headers):
        '''
        @see: DecoderHeader.decode
        
        @return: integer
            The content length.
        '''
        assert isinstance(headers, dict), 'Invalid headers dictionary %s' % headers
        if self.name not in headers:
            raise HeaderException(_('No ($1) available', self.name))
        val = headers[self.name]
        try:
            return int(val)
        except ValueError:
            raise HeaderException(_('Invalid content length ($1)', val))

# --------------------------------------------------------------------

@injected
class EncoderAllow(EncoderHeader):
    '''
    Implementation for the header encoder for allow.
    '''
    
    name = 'Allow'
    sepMethods = ','
    methGet = 'GET'
    methDel = 'DELETE'
    methIns = 'POST'
    methUpd = 'PUT'
    
    def __init__(self):
        assert isinstance(self.name, str), 'Invalid string %s' % self.name
        assert isinstance(self.sepMethods, str), 'Invalid string %s' % self.sepMethods
        assert isinstance(self.methGet, str), 'Invalid string %s' % self.methGet
        assert isinstance(self.methDel, str), 'Invalid string %s' % self.methDel
        assert isinstance(self.methIns, str), 'Invalid string %s' % self.methIns
        assert isinstance(self.methUpd, str), 'Invalid string %s' % self.methUpd
    
    def encode(self, headers, rsp):
        '''
        @see: EncoderHeader.encode
        '''
        assert isinstance(headers, dict), 'Invalid headers dictionary %s' % headers
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        if rsp.allows != 0:
            allow = []
            if rsp.allows & GET != 0: allow.append(self.methGet)
            if rsp.allows & DELETE != 0: allow.append(self.methDel)
            if rsp.allows & INSERT != 0: allow.append(self.methIns)
            if rsp.allows & UPDATE != 0: allow.append(self.methUpd)
            headers[self.name] = self.sepMethods.join(allow)
            
@injected
class EncoderContentLocation(EncoderHeader):
    '''
    Implementation for the header encoder for content location, this will use the response object type and if it a
    type property id reference will provide that reference to the content location header.
    '''
    
    name = 'Content-Location'
    resourcesManager = ResourcesManager
    # The resources manager used in locating the path for the reference.
     
    def __init__(self):
        assert isinstance(self.name, str), 'Invalid string %s' % self.name
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
    
    def encode(self, headers, rsp):
        '''
        @see: EncoderHeader.encode
        '''
        assert isinstance(headers, dict), 'Invalid headers dictionary %s' % headers
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        if rsp.contentLocation is not None:
            headers[self.name] = rsp.encoderPath.encode(rsp.contentLocation)

# --------------------------------------------------------------------

@injected
class DecoderAcceptContentType(DecoderHeader):
    '''
    Implementation for the header decoder for accepted content type.
    '''

    contentTypes = dict
    # The content types map.
    name = 'Accept'
    reSeparators = re.compile('[;,]{1}')
    
    def __init__(self):
        assert isinstance(self.contentTypes, dict), 'Invalid content types dictionary %s' % self.contentTypes
        assert isinstance(self.name, str), 'Invalid string %s' % self.name
        assert self.reSeparators is not None, 'Invalid pattern %s' % self.reSeparators
        self.contentTypesList = list(self.contentTypes)

    def decode(self, req):
        '''
        @see: DecoderHeader.decode
        '''
        assert isinstance(req, RequestHTTP), 'Invalid HTTP request %s' % req
        if self.name in req.headers:
            req.accContentTypes = []
            vals = self.reSeparators.split(req.headers[self.name])
            for val in vals:
                contentType = findInValues(self.contentTypes, val)
                if contentType is not None: req.accContentTypes.append(contentType)
        else:
            req.accContentTypes = self.contentTypesList

# --------------------------------------------------------------------

@injected
class DecoderAcceptCharSet(DecoderHeader):
    '''
    Implementation for the header decoder for accepted content type.
    '''

    charSets = dict
    # The character set map.
    name = 'Accept-Charset'
    reSeparators = re.compile('[;,]{1}')
    
    def __init__(self):
        assert isinstance(self.charSets, dict), 'Invalid char sets dictionary %s' % self.charSets
        assert isinstance(self.name, str), 'Invalid string %s' % self.name
        assert self.reSeparators is not None, 'Invalid pattern %s' % self.reSeparators
        self.charSetsList = list(self.charSets.keys())

    def decode(self, req):
        '''
        @see: DecoderHeader.decode
        '''
        assert isinstance(req, RequestHTTP), 'Invalid HTTP request %s' % req
        if self.name in req.headers:
            req.accCharSets = []
            vals = self.reSeparators.split(req.headers[self.name])
            for val in vals:
                charSet = findInValues(self.charSets, val)
                if charSet is not None: req.accCharSets.append(charSet)
        else:
            req.accCharSets = self.charSetsList
