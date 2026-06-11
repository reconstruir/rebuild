#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler

from .recipe_cli_command import recipe_cli_command

class recipe_command_handler(bcli_command_handler):

  def name(self):
    return 'recipe'

  def _command_find(self, where, options):
    return recipe_cli_command.find(where)

  def _command_fix_requirements_versions(self, where, python_version, options):
    return recipe_cli_command.fix_requirements_versions(where, python_version)
