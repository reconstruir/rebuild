#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import string_util

class hook_caca_loader_registry(object):

  _registry = {}
  
  @classmethod
  def register_hook_caca_loader_class(clazz, registree):
    name = registree.__name__
    existing = clazz._registry.get(name, None)
    if existing:
      assert False
      return
    clazz._registry[name] = registree
    if name.startswith('hook_caca_loader_'):
      name_no_hook_caca_loader = string_util.remove_head(name, 'hook_caca_loader_')
      clazz._registry[name_no_hook_caca_loader] = registree
    
  @classmethod
  def get(clazz, class_name):
    return clazz._registry.get(class_name, None)
