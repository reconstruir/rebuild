#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class recipe_step(namedtuple('recipe_step', 'name,values')):

  def __new__(clazz, name, values):
    return clazz.__bases__[0].__new__(clazz, name, values)
