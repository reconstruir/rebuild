#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.common import object_util, string_util
from .Step import Step
from .step_registry import step_register, step_registry

class step_description(object):

  def __init__(self, step_class, args = {}):
    assert isinstance(args, dict)
    self.step_class = step_class
    self.args = args

  def __str__(self):
    return '%s:%s' % (str(self.step_class), str(self.args))

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  @classmethod
  def parse_descriptions(self, items):
    result = []
    current_desc = None
    for item in items:
      if isinstance(item, step_register):
        current_desc = step_description(item, {})
        result.append(current_desc)
      elif string_util.is_string(item):
        step_class = step_registry.get(item)
        if not step_class:
          raise RuntimeError('no such step class: %s' % (item))
        current_desc = step_description(step_class, {})
        result.append(current_desc)
      else:
        assert current_desc
        assert isinstance(item, dict)
        current_desc.args.update(copy.deepcopy(item))
    return result

  @classmethod
  def is_step_description(clazz, o):
    return isinstance(o, step_description)

  @classmethod
  def is_step_description_list(clazz, o):
    return object_util.is_homogeneous(o, step_description)
