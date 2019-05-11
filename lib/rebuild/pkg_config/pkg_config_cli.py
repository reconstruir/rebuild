#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse

from rebuild.pkg_config import pkg_config
from bes.common import algorithm, string_util, table as caca_table
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
    command_group.add_argument('--cflags', nargs = '+', action = 'store',
                               help = 'Print the cflags for the given modules.')
    command_group.add_argument('--print-requires', nargs = '+', action = 'store',
                               help = 'Print the requires property for the given modules.')
    self.pc = caca_pkg_config(self.PKG_CONFIG_PATH.path)
    
  def main(self):
    args = self.parser.parse_args()

    if args.list_all:
      return self._command_list_all()
    elif args.modversion:
      return self._command_modversion(args.modversion)
    elif args.cflags:
      return self._command_cflags(args.cflags)
    elif args.print_requires:
      return self._command_print_requires(args.print_requires)
    return 0

  def _command_list_all(self):
    all_modules = self.pc.list_all()
    table = text_table(data = all_modules)
    print(str(table))
    return 0
  
  def _command_modversion(self, module_names):
    if not self._check_modules_exist(module_names):
      return 1
    for name in module_names:
      version = self.pc.module_version(name)
      print(version)
    return 0
  
  def _command_cflags(self, module_names):
    if not self._check_modules_exist(module_names):
      return 1
    cflags = []
    for name in module_names:
      cflags.extend(self.pc.module_cflags(name))
    cflags = algorithm.unique(cflags)
    print(' '.join(cflags))
    return 0

  def _command_print_requires(self, module_names):
    if not self._check_modules_exist(module_names):
      return 1
    for name in module_names:
      poto_requires = self.pc.module_requires(name)
      for req in poto_requires:
        #print('%s: %s' % (name, req))
        print(req)
    return 0
  
  def _check_modules_exist(self, module_names):
    result = True
    for name in module_names:
      if not self.pc.module_exists(name):
        result = False
        print('''Package %s was not found in the pkg-config search path.
Perhaps you should add the directory containing `%s.pc'
to the PKG_CONFIG_PATH environment variable
No package '%s' found''' % (name, name, name))
    return result
  
  @classmethod
  def run(clazz):
    raise SystemExit(pkg_config_cli().main())
