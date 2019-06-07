#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from collections import namedtuple

from bes.compat.StringIO import StringIO
from bes.common.string_util import string_util
from bes.common.point import point
from bes.system.log import log
from bes.enum.flag_enum import flag_enum
from bes.text.lexer_token import lexer_token
from bes.enum.enum import enum

from collections import namedtuple

class upstream_version_lexer(object):

  TOKEN_DONE = 'done'
  TOKEN_NUMBER = 'number'
  TOKEN_PUNCTUATION = 'punctuation'
  TOKEN_SPACE = 'space'
  TOKEN_STRING = 'string'
  TOKEN_TEXT = 'text'

  EOS = '\0'

  def __init__(self, log_tag):
    log.add_logging(self, tag = log_tag)

    self._buffer = None
    
    self.STATE_BEGIN = _state_begin(self)
    self.STATE_DONE = _state_done(self)
    self.STATE_NUMBER = _state_number(self)
    self.STATE_PUNCTUATION = _state_punctuation(self)
    self.STATE_TEXT = _state_text(self)

    self.state = self.STATE_BEGIN

  def _run(self, text):
    self.log_d('_run() text=\"%s\")' % (text))
    assert self.EOS not in text
    self.position = point(1, 1)
    for c in self._chars_plus_eos(text):
      cr = self._char_type(c)
      if cr.ctype == self._char_types.UNKNOWN:
        raise RuntimeError('unknown character: \"%s\"' % (c))
      tokens = self.state.handle_char(cr)
      for token in tokens:
        self.log_d('tokenize: new token: %s' % (str(token)))
        yield token
      self.position = point(self.position.x + 0, self.position.y)
    assert self.state == self.STATE_DONE
    yield lexer_token(self.TOKEN_DONE, None, self.position)
      
  @classmethod
  def tokenize(clazz, text, log_tag):
    return clazz(log_tag)._run(text)

  @classmethod
  def _char_to_string(clazz, c):
    if c == clazz.EOS:
      return 'EOS'
    else:
      return c
  
  def change_state(self, new_state, cr):
    assert new_state
    if new_state == self.state:
      return
    self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__,
                                                   new_state.__class__.__name__,
                                                   new_state._make_log_attributes(cr, include_state = False)))
    self.state = new_state

  @classmethod
  def _chars_plus_eos(self, text):
    for c in text:
      yield c
    yield self.EOS

  def make_token_text(self):
    return lexer_token(self.TOKEN_TEXT, self.buffer_value(), self.position)
      
  def make_token_number(self):
    return lexer_token(self.TOKEN_NUMBER, int(self.buffer_value()), self.position)
      
  def make_token_punctuation(self):
    return lexer_token(self.TOKEN_PUNCTUATION, self.buffer_value(), self.position)
      
  def buffer_reset(self, c = None):
    self._buffer = StringIO()
    if c:
      self.buffer_write(c)
      
  def buffer_reset_with_quote(self, c):
    assert c in [ self.SINGLE_QUOTE_CHAR, self.DOUBLE_QUOTE_CHAR ]
    self.buffer_reset()
    self.buffer_write_quote(c)
      
  def buffer_write(self, c):
    assert c != self.EOS
    self._buffer.write(c)

  def buffer_value(self):
    return self._buffer.getvalue()
    
  def buffer_write_quote(self, c):
    assert c in [ self.SINGLE_QUOTE_CHAR, self.DOUBLE_QUOTE_CHAR ]
    if self._keep_quotes:
      if self._escape_quotes:
        self.buffer_write('\\')
      self.buffer_write(c)

  class _char_types(enum):
    EOS = 1
    NUMBER = 2
    PUNCTUATION = 3
    TEXT = 4
    UNKNOWN = 5

  _char_result = namedtuple('_char_result', 'char, ctype')

  @classmethod
  def _char_type(clazz, c):
    if c in string.punctuation:
      return clazz._char_result(clazz._char_to_string(c), clazz._char_types.PUNCTUATION)
    elif c.isdigit():
      return clazz._char_result(clazz._char_to_string(c), clazz._char_types.NUMBER)
    elif c.isalpha():
      return clazz._char_result(clazz._char_to_string(c), clazz._char_types.TEXT)
    elif c == clazz.EOS:
      return clazz._char_result(clazz._char_to_string(c), clazz._char_types.EOS)
    else:
      return clazz._char_result(clazz._char_to_string(c), clazz._char_types.UNKNOWN)
      
class _state(object):

  def __init__(self, lexer):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (lexer.__class__.__name__, self.name))
    self.lexer = lexer
  
  def handle_char(self, c):
    raise RuntimeError('unhandled handle_char(%c) in state %s' % (self.name))

  def log_handle_char(self, cr):
    try:
      buffer_value = string_util.quote(self.lexer.buffer_value())
    except AttributeError as ex:
      buffer_value = 'None'
    self.log_d('handle_char() %s' % (self._make_log_attributes(cr)))
  
  def _make_log_attributes(self, cr, include_state = True):
    attributes = []
    if include_state:
      attributes.append('state=%s' % (self.name))
    attributes.append('c=|%s(%s)|' % (cr.char, self.lexer._char_types.value_to_name(cr.ctype)))
    try:
      attributes.append('buffer=%s' % (string_util.quote(self.lexer.buffer_value())))
    except AttributeError as ex:
      attributes.append('buffer=None')
    return ' '.join(attributes)
  
class _state_begin(_state):
  def __init__(self, lexer):
    super(_state_begin, self).__init__(lexer)

  def handle_char(self, cr):
    self.log_handle_char(cr)
    new_state = None
    tokens = []
    if cr.ctype == self.lexer._char_types.TEXT:
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_TEXT
    elif cr.ctype == self.lexer._char_types.NUMBER:
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_NUMBER
    elif cr.ctype == self.lexer._char_types.PUNCTUATION:
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PUNCTUATION
    elif cr.ctype == self.lexer._char_types.EOS:
      new_state = self.lexer.STATE_DONE
    else:
      raise RuntimeError('unexpected char %s in state %s' % (cr, self.lexer.state))
    self.lexer.change_state(new_state, cr)
    return tokens

class _state_number(_state):
  def __init__(self, lexer):
    super(_state_number, self).__init__(lexer)

  def handle_char(self, cr):
    self.log_handle_char(cr)
    new_state = None
    tokens = []
    if cr.ctype == self.lexer._char_types.TEXT:
      tokens.append(self.lexer.make_token_number())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_TEXT
    elif cr.ctype == self.lexer._char_types.NUMBER:
      self.lexer.buffer_write(cr.char)
      new_state = self.lexer.STATE_NUMBER
    elif cr.ctype == self.lexer._char_types.PUNCTUATION:
      tokens.append(self.lexer.make_token_number())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PUNCTUATION
    elif cr.ctype == self.lexer._char_types.EOS:
      tokens.append(self.lexer.make_token_number())
      new_state = self.lexer.STATE_DONE
    else:
      raise RuntimeError('unexpected char %s in state %s' % (cr, self.lexer.state))
    self.lexer.change_state(new_state, cr)
    return tokens

class _state_text(_state):
  def __init__(self, lexer):
    super(_state_text, self).__init__(lexer)

  def handle_char(self, cr):
    self.log_handle_char(cr)
    new_state = None
    tokens = []
    if cr.ctype == self.lexer._char_types.TEXT:
      self.lexer.buffer_write(cr.char)
      new_state = self.lexer.STATE_TEXT
    elif cr.ctype == self.lexer._char_types.NUMBER:
      tokens.append(self.lexer.make_token_text())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_NUMBER
    elif cr.ctype == self.lexer._char_types.PUNCTUATION:
      tokens.append(self.lexer.make_token_text())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PUNCTUATION
    elif cr.ctype == self.lexer._char_types.EOS:
      tokens.append(self.lexer.make_token_text())
      new_state = self.lexer.STATE_DONE
    else:
      raise RuntimeError('unexpected char %s in state %s' % (cr, self.lexer.state))
    self.lexer.change_state(new_state, cr)
    return tokens

class _state_punctuation(_state):
  def __init__(self, lexer):
    super(_state_punctuation, self).__init__(lexer)

  def handle_char(self, cr):
    self.log_handle_char(cr)
    new_state = None
    tokens = []
    if cr.ctype == self.lexer._char_types.TEXT:
      tokens.append(self.lexer.make_token_punctuation())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_TEXT
    elif cr.ctype == self.lexer._char_types.NUMBER:
      tokens.append(self.lexer.make_token_punctuation())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_NUMBER
    elif cr.ctype == self.lexer._char_types.PUNCTUATION:
      self.lexer.buffer_write(cr.char)
      new_state = self.lexer.STATE_PUNCTUATION
    elif cr.ctype == self.lexer._char_types.EOS:
      tokens.append(self.lexer.make_token_punctuation())
      new_state = self.lexer.STATE_DONE
    else:
      raise RuntimeError('unexpected char %s in state %s' % (cr, self.lexer.state))
    self.lexer.change_state(new_state, cr)
    return tokens
  
class _state_done(_state):
  def __init__(self, lexer):
    super(_state_done, self).__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
