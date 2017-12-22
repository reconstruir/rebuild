#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_result

class test_loaded_step2(step):
  def __init__(self):
    super(test_loaded_step2, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'bool_value bool'
  
  def execute(self, script, env, args):
    return step_result(True)
