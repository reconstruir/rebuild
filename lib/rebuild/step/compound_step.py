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
#      step.update_args(copy.deepcopy(super(compound_step, self).global_args()))
      step.update_args(step.global_args())
      step.update_args(self.args)
      self.steps.append(step)

  @classmethod
  def parse_step_args(clazz, script, env, args):
    args = copy.deepcopy(args)
    for step_class in clazz.__steps__:
      parsed_args = step_class.parse_step_args(script, env, args)
      args.update(parsed_args)
    return args

  @classmethod
  def argspec(clazz):
    result = {}
    for step_class in clazz._get_compound_classes():
      result.update(step_class.argspec() or {})
    return result

  @classmethod
  def global_args(clazz):
    args = copy.deepcopy(super(compound_step, clazz).global_args())
    for step_class in clazz.__steps__:
      args.update(step_class.global_args())
    return args

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
      result = step.execute(script, env, dict_util.combine(args, output))
      output.update(result.output or {})
      if not result.success:
        return step_result(False,
                           message = result.message,
                           failed_step = step,
                           output = output)
    return step_result(True, output = output)
  
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
