#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from bes.compat import StringIO
from bes.text import comments
from collections import namedtuple
from bes.common import check, string_util, type_checked_list
from .requirement import requirement
from .build_system import build_system

class requirement_list(type_checked_list):

  def __init__(self, values = None):
    super(requirement_list, self).__init__(requirement, values = values)

  @classmethod
  def cast_entry(clazz, entry):
    if isinstance(entry, tuple):
      return requirement(*entry)
    return entry
  
  def to_string(self, delimiter = ' '):
    buf = StringIO()
    first = True
    for req in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(req))
    return buf.getvalue()

  def __str__(self):
    return self.to_string()

  @classmethod
  def parse(clazz, text, default_system_mask = None):

    text = comments.strip_line(text)
    
    STATE_NAME = 'name'
    STATE_SYSTEM_MASK = 'system_mask'
    STATE_OPERATOR = 'operator'

    state = STATE_NAME
    reqs = clazz()

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

    for token in clazz._tokenize(text):
      if state == STATE_NAME:
        if token.type == clazz._TOKEN_END:
          if state_data.name:
            reqs.append(state_data_t.make_requirement(state_data))
        elif token.type == clazz._TOKEN_NAME:
          if state_data.name:
            reqs.append(state_data_t.make_requirement(state_data))
            state_data = state_data_t()
          state_data.name = token.text
          state_data.system_mask = token.system_mask
        elif token.type == clazz._TOKEN_OPERATOR:
          state_data.operator = token.text
          state = STATE_OPERATOR
        else:
          raise RuntimeError('Unexpected token %s in state %s' % (token, state))
      elif state == STATE_OPERATOR:
        if token.type != clazz._TOKEN_VERSION:
          raise RuntimeError('Expected version instead got end of line for %s in state %s' % (token, state))
        assert state_data.name
        state_data.version = token.text
        reqs.append(state_data_t.make_requirement(state_data))
        state_data = state_data_t()
        state = STATE_NAME
        
    reqs.remove_dups()
    check.check_requirement_list(reqs)
    return reqs

  _TOKEN_NAME = 'name'
  _TOKEN_OPERATOR = 'operator'
  _TOKEN_VERSION = 'version'
  _TOKEN_END = 'end'
  _token = namedtuple('token', 'type,text,system_mask')

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
        elif last_token.type == clazz._TOKEN_OPERATOR:
          token = clazz._token(clazz._TOKEN_VERSION, word, global_mask)
        else:
          token = clazz._make_name_token(word, global_mask)
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
      name = re.sub('\((.+)\)', '', s)
    else:
      name = s
    return name, system_mask

  @classmethod
  def _name_get_system_mask(clazz, name):
    parts = re.findall('\w+\((.+)\)', name)
    if len(parts) == 1:
      return parts[0]
    return None
    
  @classmethod
  def _word_is_operator(clazz, word):
    for c in word:
      if not c in [ '=', '>', '<', '!' ]:
        return False
    return True

  def resolve(self, system):
    'Resolve requirements for the given system.'
    if not build_system.system_is_valid(system):
      raise RuntimeError('Invalid system: %s' % (system))
    return requirement_list([ req for req in iter(self) if req.system_mask == None or build_system.mask_matches(req.system_mask, system) ])
  
check.register_class(requirement_list, include_seq = False)