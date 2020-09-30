#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from bes.text.comments import comments
from collections import namedtuple
from bes.common.check import check
from bes.common.string_util import string_util
from .requirement import requirement
from .requirement_hardness import requirement_hardness

class requirement_parser(object):

  @classmethod
  def parse(clazz, text, default_system_mask = None):
    text = comments.strip_line(text, allow_quoted = False)
    
    STATE_NAME = 'name'
    STATE_SYSTEM_MASK = 'system_mask'
    STATE_OPERATOR = 'operator'

    state = STATE_NAME
    reqs = []

    class state_data_t(object):
      def __init__(self):
        self.hardness = None
        self.name = None
        self.operator = None
        self.system_mask = None
        self.version = None
        self.expression = None

      @classmethod
      def make_requirement(clazz, state_data):
        if state_data.system_mask:
          system_mask = state_data.system_mask
        else:
          system_mask = default_system_mask
        return requirement(state_data.name,
                           state_data.operator,
                           state_data.version,
                           system_mask,
                           state_data.hardness,
                           state_data.expression)
      
    state_data = state_data_t()

    tokens = clazz._tokenize(text)
    
    for token in tokens:
      if state == STATE_NAME:
        if token.type == clazz._TOKEN_END:
          if state_data.name:
            yield state_data_t.make_requirement(state_data)
        elif token.type == clazz._TOKEN_NAME:
          if state_data.name:
            yield state_data_t.make_requirement(state_data)
            state_data = state_data_t()
          system_mask, expression = clazz._parse_expression(token.system_mask)
          state_data.name = token.text
          state_data.expression = expression
          state_data.system_mask = system_mask
        elif token.type == clazz._TOKEN_OPERATOR:
          state_data.operator = token.text
          state = STATE_OPERATOR
        elif token.type == clazz._TOKEN_HARDNESS:
          state_data.hardness = token.text
          state = STATE_NAME
        else:
          raise RuntimeError('Unexpected token %s in state %s' % (token, state))
      elif state == STATE_OPERATOR:
        if token.type != clazz._TOKEN_VERSION:
          raise RuntimeError('Expected version instead got end of line for %s in state %s' % (token, state))
        assert state_data.name
        state_data.version = token.text
        yield state_data_t.make_requirement(state_data)
        state_data = state_data_t()
        state = STATE_NAME

  _TOKEN_NAME = 'name'
  _TOKEN_OPERATOR = 'operator'
  _TOKEN_HARDNESS = 'hardness'
  _TOKEN_VERSION = 'version'
  _TOKEN_END = 'end'
  _token = namedtuple('token', 'type, text, system_mask')

  @classmethod
  def _tokenize(clazz, text):
    num_colon = text.count(':')
    if num_colon > 1:
      raise ValueError('Invalid text - only one colon is allowed: %s' % (text))
    elif num_colon == 0:
      global_mask = None
      req_text = text
    else:
      assert num_colon == 1
      left, _, right = text.partition(':')
      global_mask = left.strip()
      req_text = right.strip()
      
    last_token = None
    for word in string_util.split_by_white_space(req_text):
      if last_token:
        if clazz._word_is_operator(word):
          token  = clazz._token(clazz._TOKEN_OPERATOR, word, global_mask)
        elif clazz._word_is_hardness(word):
          token  = clazz._token(clazz._TOKEN_HARDNESS, word, global_mask)
        elif last_token.type == clazz._TOKEN_OPERATOR:
          token = clazz._token(clazz._TOKEN_VERSION, word, global_mask)
        else:
          token = clazz._make_name_token(word, global_mask)
      else:
        if clazz._word_is_hardness(word):
          token  = clazz._token(clazz._TOKEN_HARDNESS, word, global_mask)
        else:
          token = clazz._make_name_token(word, global_mask)
      yield token
      last_token = token
    yield clazz._token(clazz._TOKEN_END, None, None)

  @classmethod
  def _make_name_token(clazz, word, global_mask):
    name, system_mask = clazz._parse_name_and_system_mask(word)
    return clazz._token(clazz._TOKEN_NAME, name, system_mask or global_mask)
    
  @classmethod
  def _parse_name_and_system_mask(clazz, s):
    system_mask = clazz._name_get_system_mask(s)
    if system_mask:
      name = re.sub(r'\((.+)\)', '', s)
    else:
      name = s
    return name, system_mask

  @classmethod
  def _name_get_system_mask(clazz, name):
    parts = re.findall(r'\w+\((.+)\)', name)
    if len(parts) == 1:
      return parts[0]
    return None
    
  @classmethod
  def _word_is_operator(clazz, word):
    for c in word:
      if not c in [ '=', '>', '<', '!' ]:
        return False
    return True

  @classmethod
  def _word_is_hardness(clazz, word):
    return requirement_hardness.is_valid(word.upper())

  @classmethod
  def _parse_expression(clazz, s):
    if not s:
      return None, None
    first_parentesis = s.find('(')
    if first_parentesis < 0:
      return s, None
    second_parentesis = s.find(')', first_parentesis + 1)
    if second_parentesis < 0:
      raise ValueError('Invalid expression: {}'.format(s))
    expression = s[first_parentesis + 1 : second_parentesis]
    text = s[0:first_parentesis]
    return text, expression
