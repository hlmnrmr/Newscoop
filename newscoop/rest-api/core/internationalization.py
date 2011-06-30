'''
Created on May 26, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides internationalization support.
'''

import re
from _pyio import StringIO

# --------------------------------------------------------------------

# The prefix that is used for marking the place holders
MARK_PLACE_HOLDER = '$'
MARK_PLACE_LENGHT = len(MARK_PLACE_HOLDER)

# The pattern used for split the parameter calls.
REGEX_ID = re.compile('[1-9][0-9]*')

# --------------------------------------------------------------------

class Message:
    '''
    Maps the data required for a message.
    '''
    
    def __init__(self, default, msg, args):
        '''
        Provides a wrapping of the message which will be used as a key.
        
        @param default: string
            A default compiled message.
        @param msg: string
            The message (that is in English) to be used as a key, this message
            has to contain as many place holders (ex: $1, $2 ...) as there are 
            arguments.
        @param args: list 
            The arguments to be used instead of the place holders in the message.
        '''
        self.default = default
        self.msg = msg
        self.args = args
        
# --------------------------------------------------------------------

def msg(msg, *args):
    '''
    Provides a wrapping of the message which will be used as a key.
    The wrapped message will have the ability to be translated.
    
    @param msg: string
        The message (that is in English) to be used as a key, this message
        has to contain as many place holders (ex: $1, $2 ...) as there are 
        arguments.
    @param *args: list 
        The arguments to be used instead of the place holders in the message.
    '''
    assert isinstance(msg, str), 'The msg (message key) needs to be a string'
    
    compiled = StringIO()
    search, index = True, 0
    while search:
        k = msg.find(MARK_PLACE_HOLDER, index)
        if k > index:
            idGr = REGEX_ID.search(msg, k + MARK_PLACE_LENGHT)
            if idGr is None:
                raise AssertionError('Could not locate any valid id at index ' + str(k + MARK_PLACE_LENGHT))
            
            id = int(idGr.group(0)) - 1
            compiled.write(msg[index:k])
            try:
                compiled.write(str(args[id]))
            except IndexError:
                raise AssertionError('Could not locate a parameter for id ' + MARK_PLACE_HOLDER + str(id + 1))
            
            index = idGr.end(0)
        else:
            search = False
            
    if index < len(msg):
        compiled.write(msg[index:])
        
    return Message(compiled.getvalue(), msg, args)

# --------------------------------------------------------------------

