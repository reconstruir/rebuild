#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from .step_registry import step_registry
from collections import namedtuple

class step_description(namedtuple('step_description', 'step_class,args')):

  def __new__(clazz, step_class, args = None):
    args = args or {}
    check.check_dict(args)
    return clazz.__bases__[0].__new__(clazz, step_class, args)
  
  def __str__(self):
    return '%s:%s' % (str(self.step_class), str(self.args))

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  @classmethod
  def parse_description(self, text):
    check.check_string(text)
    step_class = step_registry.get(text)
    if not step_class:
      raise RuntimeError('no such step class: %s' % (text))
    return step_description(step_class)

check.register_class(step_description)
