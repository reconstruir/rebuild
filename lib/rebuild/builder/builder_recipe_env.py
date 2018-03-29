#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

class builder_recipe_env(object):

  def __init__(self):
    pass

  @classmethod
  def args(clazz, **kargs):
    return copy.deepcopy(kargs)
