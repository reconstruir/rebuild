#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.recipe.value import hook

class test_loaded_hook2(hook):

  def execute(self, script, env, args):
    return self.result(True)
