#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.common import read_only_dict, string_util
from collections import namedtuple

class step_registry(object):

  _data = namedtuple('_data', 'clazz,argspec')
  
  _registry = {}
  
  @classmethod
  def register_step_class(clazz, registree):
    name = registree.__name__
    existing = clazz._registry.get(name, None)
    if existing:
      return
    data = clazz._data(registree, read_only_dict(copy.deepcopy(registree.argspec() or {})))
    clazz._registry[name] = data
    if name.startswith('step_'):
      name_no_step = string_util.remove_head(name, 'step_')
      clazz._registry[name_no_step] = data
    
  @classmethod
  def get(clazz, class_name):
    return clazz._registry.get(class_name, None)
