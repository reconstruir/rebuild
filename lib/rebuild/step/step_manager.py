#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# TODO
# add argument checking/validation

import copy
from abc import abstractmethod
from bes.common import dict_util
from bes.common import check_type
from bes.system import log

from rebuild.base import build_blurb

from .compound_step import compound_step
from .step import step
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

  def _add_step(self, s):
    if not isinstance(s, step):
      raise RuntimeError('step must be an instance of step instead of %s' % (type(s)))
    s.tag = self._tag
    self._steps.append(s)
    return s

  def add_step(self, description, script, env):
    assert isinstance(description.args, dict)
    assert step_description.is_step_description(description)
    s = description.step_class()
    global_args = s.global_args()
    parsed_args = description.step_class.parse_step_args(script, env, copy.deepcopy(description.args))
    if not isinstance(parsed_args, dict):
      raise RuntimeError('%s.parse_step_args() needs to return a dict instead of \"%s\"' % (description.step_class.__name__, type(parsed_args).__name__))
    s.args = dict_util.combine(global_args, parsed_args)
    return self._add_step(s)

  def add_steps(self, descriptions, script, env):
    assert step_description.is_step_description_list(descriptions)
    for description in descriptions:
      self.add_step(description, script, env)

  def add_step_v2(self, description, script, env):
    assert isinstance(description.args, dict)
    assert step_description.is_step_description(description)
    s = description.step_class()
    global_args = s.global_args()
    parsed_args = description.step_class.parse_step_args(script, env, copy.deepcopy(description.args))
    if not isinstance(parsed_args, dict):
      raise RuntimeError('%s.parse_step_args() needs to return a dict instead of \"%s\"' % (description.step_class.__name__, type(parsed_args).__name__))
    s.args = dict_util.combine(global_args, parsed_args)
    return self._add_step(s)

  def add_steps_v2(self, descriptions, script, env):
    check_type.check_recipe_step_list(descriptions, 'descriptions')
    for description in descriptions:
      self.add_step_v2(description, script, env)

  def execute(self, script, env, args):
    output = {}
    for s in self._steps:
      step_args = dict_util.combine(args, s.args, output)
      result = s.execute(script, env, step_args)
      output.update(result.output or {})
      if not result.success:
        return step_result(False, message = result.message, failed_step = s, output = output)
    return step_result(True, output = output)

  def step_list(self, args):
    'Return a list of 2 tuples.  Each tuple has ( step, args )'
    result = []
    for s in self._steps:
      result.append((s, dict_util.combine(args, s.args)))
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
    
