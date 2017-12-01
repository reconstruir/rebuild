#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.common import check_type, object_util, string_util
from .step_registry import step_registry
from .step_registry import step_register_meta

class step_description(object):

  def __init__(self, step_class, args = {}, argspec = None):
    assert isinstance(args, dict)
    self.step_class = step_class
    self.args = args
    self.argspec = argspec or {}

  def __str__(self):
    return '%s:%s:%s' % (str(self.step_class), str(self.args), self.argspec)

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  @classmethod
  def parse_descriptions(self, items):
    result = []
    current_desc = None
    for item in items:
      if isinstance(item, step_register_meta):
        current_desc = step_description(item, {})
        result.append(current_desc)
      elif string_util.is_string(item):
        step_class = step_registry.get(item)
        if not step_class:
          raise RuntimeError('no such step class: %s' % (item))
        current_desc = step_description(step_class.clazz, args = {}, argspec = step_class.argspec)
        result.append(current_desc)
      else:
        assert current_desc
        assert isinstance(item, dict)
        current_desc.args.update(copy.deepcopy(item))
    return result

  @classmethod
  def parse_description(self, text):
    check_type.check_string(text, 'text')
    step_class = step_registry.get(text)
    if not step_class:
      raise RuntimeError('no such step class: %s' % (text))
    desc = step_description(step_class.clazz, args = {}, argspec = step_class.argspec)
    return desc

  @classmethod
  def is_step_description(clazz, o):
    return isinstance(o, step_description)

  @classmethod
  def is_step_description_list(clazz, o):
    return object_util.is_homogeneous(o, step_description)
