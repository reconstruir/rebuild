#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import os

from bes.common.check import check

from .recipe_cli_command import recipe_cli_command
from rebuild.builder.builder_config import builder_config

class recipe_cli_args(object):

  def __init__(self):
    pass
  
  def recipe_add_args(self, subparser):

    default_where = os.getcwd()
    
    # find
    p = subparser.add_parser('find', help = 'Find recipes.')
    p.add_argument('where', action = 'store', default = [ default_where ], nargs = '*',
                   help = 'Where to look for recipes. [ {} ]'.format(default_where))
    
    # fix_requirements_versions
    p = subparser.add_parser('fix_requirements_versions', help = 'Fix the requirements versions.')
    p.add_argument('where', action = 'store', default = [ default_where ], nargs = '*',
                   help = 'Where to look for recipes. [ {} ]'.format(default_where))
    p.add_argument('--python-version', action = 'store', default = builder_config.DEFAULT_PYTHON_VERSION,
                   help = 'The version of python to use. [ {} ]'.format(builder_config.DEFAULT_PYTHON_VERSION))
    
  def _command_find(self, where):
    return recipe_cli_command.find(where)

  def _command_fix_requirements_versions(self, where, python_version):
    return recipe_cli_command.fix_requirements_versions(where, python_version)
  
