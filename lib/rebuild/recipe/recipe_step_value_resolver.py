#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check_type

class recipe_step_value_resolver(object):

  def __init__(self):
    self._values = {}

  def add_value(self, value):
    check_type.check_recipe_step_value(value, 'value')
    if not value.key in self._values:
      self._values[value.key] = []
    self._values[value.key].append(value)
