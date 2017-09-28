#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from bes.common import algorithm, object_util, string_util
from collections import namedtuple
from bes.compat import StringIO
from System import System

class requirement(namedtuple('requirement', 'name,operator,version,system_mask')):

  def __new__(clazz, name, operator, version, system_mask):
    assert name
    assert name == str(name)
    name = str(name)
    if operator:
      assert operator == str(operator)
      operator = str(operator)
    if version:
      assert version == str(version)
      version = str(version)
    if system_mask:
      assert system_mask == str(system_mask)
      system_mask = str(system_mask)
    return clazz.__bases__[0].__new__(clazz, name, operator, version, system_mask)

  def __str__(self):
    buf = StringIO()
    buf.write(self.name)
    if self.system_mask and self.system_mask != 'all':
      buf.write('(')
      buf.write(self.system_mask)
      buf.write(')')
    if self.operator:
      buf.write(' ')
      buf.write(self.operator)
      buf.write(' ')
      buf.write(self.version)
    return buf.getvalue()

  @classmethod
  def requirement_list_to_string(clazz, reqs):
    assert clazz.is_requirement_list(reqs)
    return ' '.join(str(req) for req in reqs)

  @classmethod
  def parse(clazz, text, default_system_mask = None):

    STATE_NAME = 'name'
    STATE_SYSTEM_MASK = 'system_mask'
    STATE_OPERATOR = 'operator'

    state = STATE_NAME
    reqs = []

    class state_data_t(object):
      def __init__(self):
        self.name = None
        self.operator = None
        self.version = None
        self.system_mask = None

      @classmethod
      def make_requirement(clazz, state_data):
        if state_data.system_mask:
          system_mask = state_data.system_mask
        else:
          system_mask = default_system_mask
        return requirement(state_data.name, state_data.operator, state_data.version, system_mask)
      
    state_data = state_data_t()

    for token in clazz.__tokenize(text):
      if state == STATE_NAME:
        if token.type == clazz.__TOKEN_END:
          if state_data.name:
            reqs.append(state_data_t.make_requirement(state_data))
        elif token.type == clazz.__TOKEN_NAME:
          if state_data.name:
            reqs.append(state_data_t.make_requirement(state_data))
            state_data = state_data_t()
          state_data.name = token.text
          state_data.system_mask = token.system_mask
        elif token.type == clazz.__TOKEN_OPERATOR:
          state_data.operator = token.text
          state = STATE_OPERATOR
        else:
          raise RuntimeError('Unexpected token %s in state %s' % (token, state))
      elif state == STATE_OPERATOR:
        if token.type != clazz.__TOKEN_VERSION:
          raise RuntimeError('Expected version instead got end of line for %s in state %s' % (token, state))
        assert state_data.name
        state_data.version = token.text
        reqs.append(state_data_t.make_requirement(state_data))
        state_data = state_data_t()
        state = STATE_NAME

    return algorithm.unique(reqs)

  __TOKEN_NAME = 'name'
  __TOKEN_OPERATOR = 'operator'
  __TOKEN_VERSION = 'version'
  __TOKEN_END = 'end'
  __token = namedtuple('token', 'type,text,system_mask')

  @classmethod
  def __tokenize(clazz, text):
    last_token = None

    def __make_name_token(word):
      name, system_mask = clazz.__parse_name_and_system_mask(word)
      return clazz.__token(clazz.__TOKEN_NAME, name, system_mask)
    
    for word in string_util.split_by_white_space(text):
      if last_token:
        if clazz.__word_is_operator(word):
          token  = clazz.__token(clazz.__TOKEN_OPERATOR, word, None)
        elif last_token.type == clazz.__TOKEN_OPERATOR:
          token = clazz.__token(clazz.__TOKEN_VERSION, word, None)
        else:
          token = __make_name_token(word)
      else:
        token = __make_name_token(word)
      yield token
      last_token = token
    yield clazz.__token(clazz.__TOKEN_END, None, None)

  @classmethod
  def __parse_name_and_system_mask(clazz, s):
    system_mask = clazz.__name_get_system_mask(s)
    if system_mask:
      name = re.sub('\((.+)\)', '', s)
    else:
      name = s
    return name, system_mask

  @classmethod
  def __name_get_system_mask(clazz, name):
    parts = re.findall('\w+\((.+)\)', name)
    if len(parts) == 1:
      return parts[0]
    return None
    
  @classmethod
  def __word_is_operator(clazz, word):
    for c in word:
      if not c in [ '=', '>', '<', '!' ]:
        return False
    return True
  
  @classmethod
  def is_requirement_list(clazz, o):
    return object_util.is_homogeneous(o, requirement)

  @classmethod
  def is_requirement(clazz, o):
    return isinstance(o, requirement)
    
  def to_string_colon_format(self):
    req_no_system_mask = requirement(self.name, self.operator, self.version, None)
    return '%s: %s' % (self.system_mask or 'all', str(req_no_system_mask))

  @classmethod
  def resolve_requirements(clazz, requirements, system):
    'Resolve requirements for the given system.'
    if not System.system_is_valid(system):
      raise RuntimeError('Invalid system: %s' % (system))
    if not clazz.is_requirement_list(requirements):
      raise RuntimeError('requirements should be a list of requirement objects: %s' % (str(requirements)))
    return [ req for req in requirements if req.system_mask == None or System.mask_matches(req.system_mask, system) ]
