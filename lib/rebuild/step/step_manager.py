#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from abc import abstractmethod
from bes.common import algorithm, check, dict_util
from bes.system import log

from rebuild.base import build_blurb

from .compound_step import compound_step
from .step import step
from .step_result import step_result

class step_manager(object):

  def __init__(self, tag):
    log.add_logging(self, tag)
    build_blurb.add_blurb(self, tag)
    self._steps = []
    self._tag = tag
    self._stop_step = None

  def __iter__(self):
    return iter(self._steps)
    
  def add_steps(self, recipe_steps, script, env):
    check.check_recipe_step_list(recipe_steps)
    steps = []
    for recipe_step in recipe_steps:
      step_class = recipe_step.description.step_class
      step_instance = step_class()
      check.check_step(step_instance)
      step_instance.recipe = recipe_step
      step_instance.tag = self._tag
      steps.append(step_instance)
    self._steps = self._unroll_steps(steps)
    for step in self._steps:
      step.values = step.recipe.resolve_values(script.substitutions, env.recipe_load_env)
      
  @classmethod
  def _unroll_children_steps(clazz, step, result):
    assert isinstance(result, list)
    if isinstance(step, compound_step):
      for child in step.steps:
        clazz._unroll_children_steps(child, result)
    else:
      result.append(step)
      
  @classmethod
  def _unroll_steps(clazz, steps):
    result = []
    for s in steps:
      clazz._unroll_children_steps(s, result)
    return result
      
  def execute(self, script, env):
    script.timer.start('step_manager.execute()')
    outputs = {}
    for step in self._steps:
      script.timer.start('step %s' % (step.__class__.__name__))
      result = step.execute(script, env, step.values, outputs)
      script.timer.stop()
      outputs.update(result.outputs or {})
      if not result.success:
        script.timer.stop()
        return step_result(False, message = result.message, failed_step = result.failed_step, outputs = outputs)
    script.timer.stop()
    return step_result(True, outputs = outputs)

  def step_list(self):
    'Return a list of 2 tuples.  Each tuple has ( step, args )'
    result = []
    for s in self._steps:
      result.append((s, copy.deepcopy(s.args)))
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
    
  def sources(self):
    sources = []
    for step in self:
      for key, value in step.values.items():
        if check.is_value_base(value):
          sources.extend(value.sources())
    return algorithm.unique(sources)
  
