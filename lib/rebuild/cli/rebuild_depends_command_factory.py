#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .rebuild_depends_command_handler import rebuild_depends_command_handler

class rebuild_depends_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'depends'

  @classmethod
  def description(clazz):
    return 'Print rebuild dependency information'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    return None

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    pass

  def add_commands(self, subparsers):
    p = subparsers.add_parser('versions', help = 'Print module version information.')
    p.add_argument('-f', '--filenames', action = 'store_true', default = False,
                   help = 'Print filenames where the modules were imported from. [ False ]')
    p.add_argument('-p', '--plain', action = 'store_true', default = False,
                   help = 'Use plain formatting instead of a fancy table. [ False ]')

  def handler_class(self):
    return rebuild_depends_command_handler

  def supported_platforms(self):
    return 'all'
