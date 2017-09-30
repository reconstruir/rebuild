#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import object_util
from .step_result import step_result

class step_hook(object):

  AFTER = 'after'
  BEFORE = 'before'

  def __init__(self, hook, order):
    self.check_hook(hook)
    self.hook = hook
    self.order = order
    
  @classmethod
  def check_hook(clazz, hook):
    if not hook:
      raise RuntimeError('hook is empty.')
    if not object_util.is_callable(hooks):
      raise RuntimeError('hook is not callable: %s' % (hook.__name__))
  
  @classmethod
  def call_hook(clazz, hook, argument):
    clazz.check_hook(hook)
    hook_result = hook(argument)
    if not isinstance(hook_result, step_result):
      raise RuntimeError('hook %s did not return step_result.' % (hook.__name__))
    return hook_result

  @classmethod
  def call_hooks(clazz, hooks, argument):
    for hook in hooks:
      hook_result = clazz.call_hook(hook, argument)
      if not hook_result.success:
        return hook_result
    return step_result(True)
