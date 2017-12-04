#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_result

class test_loaded_step1(step):
  def __init__(self):
    super(test_loaded_step1, self).__init__()
    
  @classmethod
  def argspec(clazz):
    return {
      'bool_value': clazz.BOOL
    }
  
  def execute(self, script, env, args):
    return step_result(True)
