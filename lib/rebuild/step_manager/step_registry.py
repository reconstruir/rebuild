#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect
from abc import ABCMeta
from bes.common import string_util
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
    print('registree: %s' % (str(registree)))
    data = clazz._data(registree, registree.argspec())
    clazz._registry[name] = data
    if name.startswith('step_'):
      name_no_step = string_util.remove_head(name, 'step_')
      clazz._registry[name_no_step] = data
    
  @classmethod
  def get(clazz, class_name):
    return clazz._registry.get(class_name, None)

class step_register(ABCMeta):

  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    step_registry.register_step_class(clazz)
    return clazz
