#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .Step import Step
from .Step import step_result

class step_call_hooks(Step):
  'A superclass for steps that call hooks.'

  def __init__(self):
    super(step_call_hooks, self).__init__()

  def execute(self, argument):
    return self.call_hooks(argument, self.HOOKS_NAMES)

  @classmethod
  def parse_step_args(clazz, packager_env, args):
    return clazz.resolve_step_args_list(packager_env, args, clazz.HOOKS_NAMES)

  TEMPLATE = '''
from rebuild.step_manager import step_call_hooks
class %s(step_call_hooks):
  '%s.'
  HOOKS_NAMES = '%s'
  def __init__(self):
    super(%s, self).__init__()
'''
  @classmethod
  def make_class(clazz, class_name, hooks_names, comment):
    code = clazz.TEMPLATE % (class_name, comment, hooks_names, class_name)
    tmp_globals = {}
    tmp_locals = {}
    exec(code, tmp_locals, tmp_globals)
    return tmp_globals[class_name]
