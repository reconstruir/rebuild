#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from rebuild.builder.builder_config import builder_config

from .recipe_command_handler import recipe_command_handler

class recipe_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'recipe'

  @classmethod
  def description(clazz):
    return 'Recipe operations'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    return None

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    pass

  def add_commands(self, subparsers):
    default_where = os.getcwd()

    p = subparsers.add_parser('find', help = 'Find recipes.')
    p.add_argument('where', action = 'store', default = [ default_where ], nargs = '*',
                   help = 'Where to look for recipes. [ {} ]'.format(default_where))

    p = subparsers.add_parser('fix_requirements_versions',
                              help = 'Fix the requirements versions.')
    p.add_argument('where', action = 'store', default = [ default_where ], nargs = '*',
                   help = 'Where to look for recipes. [ {} ]'.format(default_where))
    p.add_argument('--python-version', action = 'store',
                   default = builder_config.DEFAULT_PYTHON_VERSION,
                   help = 'The version of python to use. [ {} ]'.format(
                     builder_config.DEFAULT_PYTHON_VERSION))

  def handler_class(self):
    return recipe_command_handler

  def supported_platforms(self):
    return 'all'
