#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.recipe.value import value_hook

class test_loaded_hook3(value_hook):
    
  def execute(self, script, env, args):
    return self.result(True)
