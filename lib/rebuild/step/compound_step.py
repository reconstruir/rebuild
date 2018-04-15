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
  def parse_step_args(clazz, script, env, values):
    values = copy.deepcopy(values)
    for step_class in clazz.__steps__:
      parsed_args = step_class.parse_step_args(script, env, values)
      values.update(parsed_args)
    return values

  @classmethod
  def define_args(clazz):
    result = {}
    for step_class in clazz._get_compound_classes():
      defs = step_class.args_definition()
      result.update(defs)
    return result

  def prepare(self, script, env, args):
    assert self.steps
    for step in self.steps:
      step.prepare(script, env, dict_util.combine(args, output))
  
  def sources(self):
    sources = []
    assert self.steps
    for step in self.steps:
      sources.append(step.sources())
    return sources

  def execute(self, script, env, args):
    assert self.steps
    output = {}
    for step in self.steps:
      script.timer.start('step %s' % (step.__class__.__name__))
      result = step.execute(script, env, dict_util.combine(args, output))
      script.timer.stop()
      output.update(result.output or {})
      if not result.success:
        return step_result(False,
                           message = result.message,
                           failed_step = step,
                           output = output)
    return step_result(True, output = output)

  @property
  def recipe(self):
    return super(compound_step, self).recipe()
  
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

  def sources_keys(self):
    keys = []
    for step in self.steps:
      keys.extend(step.sources_keys())
    return sorted(list(set(keys)))

  @classmethod
  def _get_compound_classes(clazz):
    return getattr(clazz, '__steps__', [])
