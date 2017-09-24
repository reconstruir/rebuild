#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from recipe_section import recipe_section
from recipe_values_parser import recipe_values_parser

class _state(object):

  def __init__(self, parser):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (parser.__class__.__name__, self.name))
    self.parser = parser
  
  def handle_key_value(self, token):
    raise RuntimeError('unhandled handle_key_value(%c) in state %s' % (self.name))

  def change_state(self, new_state, token):
    self.parser.change_state(new_state, 'token="%s:%s"'  % (token.type, token.value))

  def unexpected_token(self, token):
    raise RuntimeError('unexpected token in %s state: %s' % (self.name, str(token)))

class _state_expecting_header(_state):
  def __init__(self, parser):
    super(_state_expecting_header, self).__init__(parser)

  def handle_key_value(self, token):
    self.log_d('handle_key_value(%s)' % (str(token)))
    new_state = None
    strings = []
    if token.type == lexer.TOKEN_COMMENT:
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_EXPECTING_HEADER
    elif token.type == lexer.TOKEN_DONE:
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.TOKEN_STRING:
      strings = [ token.value ]
      new_state = self.parser.STATE_EXPECTING_HEADER
    else:
      self.unexpected_token(token)
    self.change_state(new_state, token)
    return strings
    
class _state_done(_state):
  def __init__(self, parser):
    super(_state_done, self).__init__(parser)

  def handle_key_value(self, token):
    self.log_d('handle_key_value(%s)' % (str(token)))
    if token.type != lexer.TOKEN_DONE:
      self.unexpected_token(token)
    self.change_state(self.parser.STATE_DONE, token)
    return []

class recipe_section_parser(object):

  def __init__(self, header_key):
    log.add_logging(self, tag = 'recipe_section_parser')
    self._header_key = header_key
    self.STATE_EXPECTING_HEADER = _state_expecting_header(self)
    self.STATE_DONE = _state_done(self)
    self.state = self.STATE_EXPECTING_HEADER

  def is_header_key(self, s):
    return s == self._header_key
    
  def run(self, text):
    self.log_d('run(%s)' % (text))

    current_recipe_section = None

    for kv in recipe_values_parser.parse(text):
      self.log_d('run(): parse: new kv=\"%s\" - current_recipe_section=%s' % (kv, current_recipe_section))
      if self.is_header_key(kv.key):
        if current_recipe_section:
          self.log_d('run(): parse: new recipe_section: %s' % (str(current_recipe_section).replace('\n', '\\n')))
          yield current_recipe_section
          current_recipe_section = None
        current_recipe_section = recipe_section(kv, [])
      else:
        current_recipe_section.values.append(kv)
    if current_recipe_section:
      self.log_d('run(): parse: new recipe_section: %s' % (str(current_recipe_section).replace('\n', '\\n')))
      yield current_recipe_section
    self.log_d('run(): done.')

  @classmethod
  def parse(clazz, text, header_key):
    return clazz(header_key).run(text)

  @classmethod
  def parse_to_list(clazz, text, header_key):
    return [ section for section in clazz.parse(text, header_key) ]
