#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from rebuild.step import variable_manager

class builder_recipe_env(object):

  def __init__(self):
    pass

  @classmethod
  def args(clazz, **kargs):
    return copy.deepcopy(kargs)

  @classmethod
  def simple_lib(clazz, name, version, revision, pkg_config_name, steps, **kargs):
    pkg_config_name = pkg_config_name or name
    args = clazz.args(
      properties = clazz.args(
        name = name,
        version = version,
        revision = revision,
        category = 'lib',
        pkg_config_name = pkg_config_name,
      ),
      steps = steps,
      **kargs)
    return lambda env: args

  @classmethod
  def add_variable(clazz, key, value):
    variable_manager.add_variable(key, value)
