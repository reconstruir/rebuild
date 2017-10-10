#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from bes.key_value import key_value_lexer as lexer, key_value

class _state(object):

  def __init__(self, parser):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (parser.__class__.__name__, self.name))
    self.parser = parser

  def handle_token(self, token):
    raise RuntimeError('unhandled handle_token(%c) in state %s' % (self.name))

  def change_state(self, new_state, token):
    self.parser.change_state(new_state, 'token="%s:%s"'  % (token.token_type, token.value))

class _state_expecting_key(_state):
  def __init__(self, parser):
    super(_state_expecting_key, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    if token.token_type == lexer.TOKEN_COMMENT:
      new_state = self.parser.STATE_EXPECTING_KEY
    elif token.token_type == lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_EXPECTING_KEY
    elif token.token_type == lexer.TOKEN_DELIMITER:
      raise RuntimeError('unexpected colon instead of key: %s' % (self.parser.text))
    elif token.token_type == lexer.TOKEN_DONE:
      new_state = self.parser.STATE_DONE
    elif token.token_type == lexer.TOKEN_STRING:
      self.parser.new_key(token.value)
      new_state = self.parser.STATE_EXPECTING_COLON
    self.change_state(new_state, token)
    
class _state_expecting_colon(_state):
  def __init__(self, parser):
    super(_state_expecting_colon, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    key_value_result = None
    if token.token_type == lexer.TOKEN_COMMENT:
      raise RuntimeError('unexpected comment instead of colon: %s' % (self.parser.text))
    elif token.token_type == lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_EXPECTING_COLON
    elif token.token_type == lexer.TOKEN_DELIMITER:
      new_state = self.parser.STATE_EXPECTING_FIRST_VALUE
    elif token.token_type == lexer.TOKEN_DONE:
      raise RuntimeError('unexpected done instead of colon: %s' % (self.parser.text))
    elif token.token_type == lexer.TOKEN_STRING:
      raise RuntimeError('unexpected string \"%s\" instead of colon: %s' % (token.value, self.parser.text))
    self.change_state(new_state, token)
    return key_value_result

class _state_expecting_first_value(_state):
  def __init__(self, parser):
    super(_state_expecting_first_value, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    key_value_result = None
    if token.token_type == lexer.TOKEN_COMMENT:
      raise RuntimeError('unexpected comment \"%s\" instead of value: %s' % (token.value, self.parser.text))
    elif token.token_type == lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_EXPECTING_FIRST_VALUE
    elif token.token_type == lexer.TOKEN_DELIMITER:
      raise RuntimeError('unexpected colon instead of value: %s' % (self.parser.text))
    elif token.token_type == lexer.TOKEN_DONE:
      raise RuntimeError('unexpected end of string instead of value: %s' % (self.parser.text))
    elif token.token_type == lexer.TOKEN_STRING:
      self.parser.new_value(token.value)
      new_state = self.parser.STATE_EXPECTING_MORE_VALUES
    self.change_state(new_state, token)
    return key_value_result
    
class _state_expecting_more_values(_state):
  def __init__(self, parser):
    super(_state_expecting_more_values, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    key_value_result = None
    if token.token_type == lexer.TOKEN_COMMENT:
      new_state = self.parser.STATE_EXPECTING_KEY
    elif token.token_type == lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_EXPECTING_MORE_VALUES
    elif token.token_type == lexer.TOKEN_DELIMITER:
      key = self.parser.pop_value()
      self.log_d('popped key: \"%s\"' % (key))
      key_value_result = self.parser.make_key_value()
      self.parser.new_key(key)
      new_state = self.parser.STATE_EXPECTING_FIRST_VALUE
    elif token.token_type == lexer.TOKEN_DONE:
      key_value_result = self.parser.make_key_value()
      new_state = self.parser.STATE_DONE
    elif token.token_type == lexer.TOKEN_STRING:
      self.log_d('new value: \"%s\"' % (token.value))
      self.parser.new_value(token.value)
      new_state = self.parser.STATE_EXPECTING_MORE_VALUES
    self.change_state(new_state, token)
    return key_value_result

class _state_done(_state):
  def __init__(self, parser):
    super(_state_done, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    if token.token_type != lexer.TOKEN_DONE:
      raise RuntimeError('unexpected token in done state: %s' % (str(token)))
    self.change_state(self.parser.STATE_DONE, token)
  
class recipe_values_parser(object):

  def __init__(self):
    log.add_logging(self, tag = 'recipe_values_parser')

    self.STATE_EXPECTING_KEY = _state_expecting_key(self)
    self.STATE_EXPECTING_FIRST_VALUE = _state_expecting_first_value(self)
    self.STATE_EXPECTING_COLON = _state_expecting_colon(self)
    self.STATE_EXPECTING_MORE_VALUES = _state_expecting_more_values(self)
    self.STATE_DONE = _state_done(self)

    self.state = self.STATE_EXPECTING_KEY

    self._key = None
    self._values = None

  def run(self, text):
    self.log_d('run(%s)' % (text))
    self.text = text

    for token in lexer.tokenize(text, ':', options = lexer.KEEP_QUOTES):
      key_value = self.state.handle_token(token)
      if key_value:
        self.log_d('run(): new key_value=\"%s\"' % (str(key_value)))
        yield key_value
    self.log_d('run(): done')
    assert self.state == self.STATE_DONE

  @classmethod
  def parse(clazz, text):
    return clazz().run(text)

  def new_key(self, key):
    self.log_d('new key: \"%s\"' % (key))
    self._key = key
    self._values = []

  def new_value(self, value):
    self.log_d('new value: \"%s\"' % (value))
    self._values.append(value)

  def make_key_value(self):
    return key_value(self._key, ' '.join(self._values))

  def pop_value(self):
    return self._values.pop()

  def change_state(self, new_state, msg):
    assert new_state
    if new_state != self.state:
      self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__, new_state.__class__.__name__, msg))
      self.state = new_state
