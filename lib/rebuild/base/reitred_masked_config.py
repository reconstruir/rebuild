#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import string_util
from bes.key_value import key_value_list, key_value_parser
from bes.text import string_list_parser
from collections import namedtuple
from bes.compat import StringIO
from rebuild.base import build_system
from .requirement import requirement
from .requirement_list import requirement_list

class reitred_masked_config(namedtuple('reitred_masked_config', 'system_mask,data')):

  def __new__(clazz, system_mask, data):
    return clazz.__bases__[0].__new__(clazz, system_mask, data)

  def __str__(self):
    buf = StringIO()
    if self.system_mask:
      buf.write(self.system_mask)
      buf.write(': ')
    buf.write(str(self.data))
    return buf.getvalue()

  @classmethod
  def parse(clazz, text, parse_func = None):
    left, delimiter, right = text.partition(':')
    if delimiter == ':':
      if left == '':
        system_mask = None
      else:
        system_mask = left
    else:
      system_mask = None
    parse_func = parse_func or clazz.parse_func_string
    data = parse_func(right.strip())
    return reitred_masked_config(system_mask, data)

  @classmethod
  def parse_key_values(clazz, text):
    try:
      return clazz.parse(text, parse_func = clazz.parse_func_key_values)
    except Exception as ex:
      print(('Caught exceptions parsing: %s' % (str(text))))
      raise

  @classmethod
  def parse_key_values_list(clazz, l):
    return [ clazz.parse_key_values(s) for s in l ]

  @classmethod
  def parse_list(clazz, text):
    return clazz.parse(text, parse_func = clazz.parse_func_string_list)

  @classmethod
  def parse_requirement(clazz, text):
    parsed = clazz.parse(text, parse_func = clazz.parse_func_requirement)
    data = []
    for req in parsed.data:
      name = req.name
      operator = req.operator
      version = req.version
      if req.system_mask == None and parsed.system_mask != None:
        system_mask = parsed.system_mask
      else:
        system_mask = req.system_mask
        if not system_mask:
          pass #system_mask = build_system.ALL
      data.append(requirement(name, operator, version, system_mask))
    return clazz(parsed.system_mask, data)
    
  @classmethod
  def parse_func_string(clazz, text):
    return text

  @classmethod
  def parse_func_key_values(clazz, text):
    return key_value_list([ kv for kv in key_value_parser.parse(text, options = key_value_parser.KEEP_QUOTES) ])

  @classmethod
  def parse_func_string_list(clazz, text):
    return [ str(s) for s in string_list_parser.parse(text, options = key_value_parser.KEEP_QUOTES) ]

  @classmethod
  def parse_func_requirement(clazz, text):
    assert ':' not in text
    return requirement_list.parse(text)

  @classmethod
  def resolve_key_values(clazz, config, system):
    if not build_system.system_is_valid(system):
      raise RuntimeError('Invalid system: %s' % (str(system)))
    result = key_value_list()
    for line in config:
      psc = clazz.parse_key_values(line)
      if build_system.mask_matches(psc.system_mask, system):
        result.extend(psc.data)
    return result

  @classmethod
  def resolve_list(clazz, config, system):
    if not build_system.system_is_valid(system):
      raise RuntimeError('Invalid system: %s' % (str(system)))
    if not isinstance(config, list):
      raise RuntimeError('config is not a list.')
    result = []
    for line in config:
      psc = clazz.parse_list(line)
      if build_system.mask_matches(psc.system_mask, system):
        result.extend(psc.data)
    return result

  @classmethod
  def resolve_key_values_to_dict(clazz, config, system):
    key_values = clazz.resolve_key_values(config, system)
    result = {}
    for kv in key_values:
      result[kv.key] = kv.value
    return result

  @classmethod
  def resolve_requirement(clazz, config, system):
    if not build_system.system_is_valid(system):
      raise RuntimeError('Invalid system: %s' % (str(system)))
    if not isinstance(config, list):
      raise RuntimeError('config is not a list.')
    result = []
    for line in config:
      psc = clazz.parse_requirement(line)
      req_list = psc.data
      assert isinstance(req_list, list)
      for req in req_list:
        # Check for a requirement specific system mask
        if req.system_mask:
          if build_system.mask_matches(req.system_mask, system):
            # Clean the original system mask since it has been resolved
            clean_req = requirement(req.name, req.operator, req.version, None)
            result.append(clean_req)
        else:
          if psc.system_mask and build_system.mask_matches(psc.system_mask, system):
            result.append(req)
    return result
