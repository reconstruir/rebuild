#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os
from bes.common import dict_util
from Step import Step
from step_result import step_result
from step_argument import step_argument

class multiple_steps(Step):

  def __init__(self):
    super(multiple_steps, self).__init__()
    self.steps = []
    for step_class in self.step_classes:
      step = step_class()
#      self.log_d('%s: multiple_steps.__init__() created %s' % (self, step))
#      step.update_args(copy.deepcopy(super(multiple_steps, self).global_args()))
      step.update_args(step.global_args())
      step.update_args(self.args)
      self.steps.append(step)

  @classmethod
  def parse_step_args(clazz, packager_env, args):
    args = copy.deepcopy(args)
    for step_class in clazz.step_classes:
      parsed_args = step_class.parse_step_args(packager_env, args)
      args.update(parsed_args)
    return args

  @classmethod
  def global_args(clazz):
    args = copy.deepcopy(super(multiple_steps, clazz).global_args())
    for step_class in clazz.step_classes:
      args.update(step_class.global_args())
    return args

  def execute(self, args):
    assert self.steps
    cloned_args = args.clone()
#    self.log_d('%s: multiple_steps.execute() steps=%s' % (self, self.steps))
    for step in self.steps:
      import inspect
      result = step.execute(cloned_args)
#      self.log_d('%s: multiple_steps.execute() executed %s => %s' % (self, step.execute, result))
      cloned_args.update_output(result.output)
      if not result.success:
        return step_result(False,
                           message = result.message,
                           failed_step = step,
                           output = cloned_args.output)
    return step_result(True, output = cloned_args.output)

  def update_args(self, args):
    super(multiple_steps, self).update_args(args)
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
