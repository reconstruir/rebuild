#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse

from rebuild.pkg_config import pkg_config
from bes.common import string_util
from bes.system import os_env_var
from bes.text import text_table

from rebuild.pkg_config import caca_pkg_config

class pkg_config_cli(object):

  PKG_CONFIG_PATH = os_env_var('PKG_CONFIG_PATH')
  
  def __init__(self):
    self.parser = argparse.ArgumentParser(description = 'Build packages.')
    command_group = self.parser.add_mutually_exclusive_group()
    command_group.add_argument('--list-all', action = 'store_true')
    command_group.add_argument('--modversion', nargs = '+', action = 'store',
                               help = 'Print the version for the given modules.')

    
  def main(self):
    args = self.parser.parse_args()

    if args.list_all:
      return self._command_list_all()
    elif args.modversion:
      return self._command_modversion(args.modversion)
    return 0

  def _command_list_all(self):
    pc = caca_pkg_config(self.PKG_CONFIG_PATH.path)
    all_modules = pc.list_all()
    table = text_table(data = all_modules, column_delimiter = ' ')
    print(str(table))
    return 0
  
  def _command_modversion(self, module_names):
    pc = caca_pkg_config(self.PKG_CONFIG_PATH.path)
    module_versions = pc.module_versions(module_names)
    rv = 0
    for name in module_names:
      if not self._print_mod_version(module_versions, name):
        rv = 1
    return rv
  
  def _print_mod_version(self, module_versions, name):
    version = module_versions[name]
    if version is None:
      print('''Package %s was not found in the pkg-config search path.
Perhaps you should add the directory containing `%s.pc'
to the PKG_CONFIG_PATH environment variable
No package '%s' found''' % (name, name, name))
      return False
    print(version)
    return True
  
  @classmethod
  def run(clazz):
    raise SystemExit(pkg_config_cli().main())
