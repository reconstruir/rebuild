#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
import os.path as path

from bes.app.bes_file_application import bes_file_application

from rebuild.recipe.recipe_command_factory import recipe_command_factory

class recipe_app(bes_file_application):

  #@abstractmethod
  def name(self):
    return 'recipe'

  #@abstractmethod
  def parser_factories(self):
    return [
      recipe_command_factory,
    ]

if __name__ == '__main__':
  sys.dont_write_bytecode = True
  sys.path.remove(path.normpath(path.dirname(__file__)))
  raise SystemExit(recipe_app.main())
