'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the converters used in parsing path and contents.
'''
from ally.core.spec.resources import Converter
import numbers

# --------------------------------------------------------------------

class Standard(Converter):
    '''
    Provides stabdard type conversion
    
    @see: Standard
    '''
    
    def normalize(self, value):
        '''
        @see: Standard.normalize
        '''
        assert isinstance(value, str), 'Invalid string value %s' % value
        return value
    
    def asString(self, objValue):
        '''
        @see: Standard.asString
        '''
        assert not objValue == None, 'No object value is provided'
        if isinstance(objValue, bool):
            return self.convertBool(objValue)
        if isinstance(objValue, int):
            return self.convertInt(objValue)
        if isinstance(objValue, numbers.Number):
            return self.convertInt(objValue)
        raise AssertionError('Invalid object value %s' % objValue)
    
    def convertBool(self, boolValue=None, parse=None):
        '''
        @see: Standard.convertBool
        '''
        assert not boolValue == None and parse == None, 'No value is provided'
        assert not boolValue != None and parse != None, 'Only one value needs to be provided'
        if boolValue is not None:
            return str(boolValue)
        return bool(parse)
    
    def convertInt(self, intValue=None, parse=None):
        '''
        @see: Standard.convertInt
        '''
        assert not intValue == None and parse == None, 'No value is provided'
        assert not intValue != None and parse != None, 'Only one value needs to be provided'
        if intValue is not None:
            return str(intValue)
        return int(parse)        
        
    def convertDecimal(self, decValue=None, parse=None):
        '''
        @see: Standard.convertDecimal
        '''
        assert not decValue == None and parse == None, 'No value is provided'
        assert not decValue != None and parse != None, 'Only one value needs to be provided'
        if decValue is not None:
            return str(decValue)
        return float(decValue)
