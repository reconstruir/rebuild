#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import string_util
from collections import namedtuple

class step_registry(object):

  _registry = {}
  
  @classmethod
  def register_step_class(clazz, registree):
    name = registree.__name__
    existing = clazz._registry.get(name, None)
    if existing:
      return
    clazz._registry[name] = registree
    if name.startswith('step_'):
      name_no_step = string_util.remove_head(name, 'step_')
      clazz._registry[name_no_step] = registree
    
  @classmethod
  def get(clazz, class_name):
    return clazz._registry.get(class_name, None)
