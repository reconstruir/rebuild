#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

class variable_manager(object):

  _variables = {}

  @classmethod
  def add_variable(clazz, key, value):
    if key in clazz._variables:
      old_value = clazz._variables[key]
      if old_value != value:
        raise RuntimeError('Variable already registered with different value: %s; old=%s; new=%s' % (key, old_value, value))
    clazz._variables[key] = value

  @classmethod
  def get_variables(clazz):
    return copy.deepcopy(clazz._variables)
