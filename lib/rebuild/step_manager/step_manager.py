#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# TODO
# add argument checking/validation

from abc import abstractmethod
from bes.common import dict_util
from bes.system import log

from rebuild import build_blurb

from .multiple_steps import multiple_steps
from .Step import Step
from .step_argument import step_argument
from .step_description import step_description
from .step_result import step_result

class step_manager(object):

  def __init__(self, tag):
    log.add_logging(self, tag)
    build_blurb.add_blurb(self, tag)
    self._steps = []
    self._args = {}
    self._tag = tag
    self._stop_step = None

  def __add_step(self, step):
    if not isinstance(step, Step):
      raise RuntimeError('step must be an instance of Step instead of %s' % (type(step)))
    step.tag = self._tag
    self._steps.append(step)
    return step

  # FIXME: only allow description
  def add_step(self, description, script):
    assert step_description.is_step_description(description)
    step = description.step_class()
    assert isinstance(description.args, dict)
    global_args = step.global_args()
    parsed_args = description.step_class.parse_step_args(script, description.args)
    if not isinstance(parsed_args, dict):
      raise RuntimeError('%s.parse_step_args() needs to return a dict instead of \"%s\"' % (description.step_class.__name__, type(parsed_args).__name__))
    step.args = dict_util.combine(global_args, parsed_args)
    return self.__add_step(step)

  def add_steps(self, descriptions, script):
    assert step_description.is_step_description_list(descriptions)
    for description in descriptions:
      self.add_step(description, script)

  def execute(self, script, env, args):
    output = {}
    for step in self._steps:
      step_args = dict_util.combine(args, step.args, output)
      result = step.execute(script, env, step_args)
      output.update(result.output or {})
      if not result.success:
        return step_result(False, message = result.message, failed_step = step, output = output)
    return step_result(True, output = output)

  def step_list(self, args):
    'Return a list of 2 tuples.  Each tuple has ( step, args )'
    result = []
    for step in self._steps:
      result.append((step, dict_util.combine(args, step.args)))
    return result

  @property
  def stop_step(self):
    return self._stop_step

  @stop_step.setter
  def stop_step(self, stop_step):
    self._stop_step = stop_step

  @property
  def has_steps(self):
    return len(self._steps) > 0
    
