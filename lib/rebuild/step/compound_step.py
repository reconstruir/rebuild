#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.common import dict_util
from .step import step
from .step_result import step_result

class compound_step(step):

  def __init__(self):
    super(compound_step, self).__init__()
    self.steps = []
    for step_class in self.__steps__:
      step = step_class()
#      self.log_d('%s: compound_step.__init__() created %s' % (self, step))
      step.update_args(self.args)
      self.steps.append(step)

  @classmethod
  def define_args(clazz):
    result = {}
    for step_class in clazz._get_compound_classes():
      defs = step_class.args_definition()
      result.update(defs)
    return result

  @property
  def recipe(self):
    assert False
    return super(compound_step, self).recipe()

  #@abstractmethod
  def execute(self, script, env, values, inputs):
    assert False
  
  @recipe.setter
  def recipe(self, recipe):
    assert recipe != None
    for step in self.steps:
      step.recipe = recipe
      
  def update_args(self, args):
    super(compound_step, self).update_args(args)
    for step in self.steps:
      step.update_args(args)

  def on_tag_changed(self):
    for step in self.steps:
      step.tag = self.tag

  @classmethod
  def _get_compound_classes(clazz):
    return getattr(clazz, '__steps__', [])
