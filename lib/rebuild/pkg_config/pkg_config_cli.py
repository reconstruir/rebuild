#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse

from rebuild.pkg_config import pkg_config
from bes.common import string_util
from bes.text import text_table

from rebuild.pkg_config import caca_pkg_config

class pkg_config_cli(object):

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
      return self._command_modversion(sorted(args.modversion))
    return 0

  def _command_list_all(self):
    all_modules = caca_pkg_config.list_all([ '/Users/ramiro/.rebuild/dev_tools/installation/lib/pkgconfig' ])
    table = text_table(data = all_modules, column_delimiter = ' ')
    print(str(table))
    return 0
  
  def _command_modversion(self, modules):
    #pkg-config --modversion glproto xcursor
    #1.4.17
    #1.1.14
    print('_command_modversion(%s)' % (modules))
    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(pkg_config_cli().main())
