#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.common import check_type, object_util, string_util
from .step_registry import step_registry
from collections import namedtuple

class step_description(namedtuple('step_description', 'step_class,args')):

  def __new__(clazz, step_class, args = None):
    args = args or {}
    assert isinstance(args, dict)
    return clazz.__bases__[0].__new__(clazz, step_class, args)
  
  def __str__(self):
    return '%s:%s' % (str(self.step_class), str(self.args))

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  @classmethod
  def parse_descriptions(self, items):
    result = []
    current_desc = None
    for item in items:
      if string_util.is_string(item):
        step_class = step_registry.get(item)
        if not step_class:
          raise RuntimeError('no such step class: %s' % (item))
        current_desc = step_description(step_class, args = {})
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
    desc = step_description(step_class)
    return desc

  @classmethod
  def is_step_description(clazz, o):
    return isinstance(o, step_description)

  @classmethod
  def is_step_description_list(clazz, o):
    return object_util.is_homogeneous(o, step_description)
check_type.register_class(step_description, include_seq = False)
