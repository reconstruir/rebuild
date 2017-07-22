#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

class variable_manager(object):

  _variables = {}

  @classmethod
  def add_variable(clazz, key, value):
    if clazz._variables.has_key(key):
      raise RuntimeError('variable already registered: %s' % (key))
    clazz._variables[key] = value

  @classmethod
  def get_variables(clazz):
    return copy.deepcopy(clazz._variables)
