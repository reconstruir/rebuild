#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import hook, step_result

class test_loaded_hook3(hook):
    
  def execute(self, script, env, args):
    return step_result(True)
