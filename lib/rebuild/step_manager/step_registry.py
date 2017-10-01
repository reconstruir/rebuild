#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class step_registry(object):

  _registry = {}
  
  @classmethod
  def register_step_class(clazz, registree):
    name = registree.__name__
    if name in clazz._registry:
      raise RuntimeError('a class named \"%s\" is already registered: %s' % (name, registree))
    clazz._registry[name] = registree
    
  @classmethod
  def get(clazz, class_name):
    return clazz._registry.get(class_name, None)

class step_register(type):

  def __new__(meta, name, bases, class_dict):
    clazz = type.__new__(meta, name, bases, class_dict)
    step_registry.register_step_class(clazz)
    return clazz
