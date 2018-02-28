#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import argparse, os.path as path
from rebuild.jail import config_file, jail
from bes.fs import file_util
from bes.system import execute, user, host

class jail_cli(object):

  def __init__(self):
    parser = argparse.ArgumentParser()
  
    subparsers = parser.add_subparsers(help = 'commands', dest = 'command')
  
    # create
    create_parser = subparsers.add_parser('create', help = 'Create a jail')
    create_parser.add_argument('location',
                               action = 'store',
                               help = 'Where to put the jail')
    create_parser.add_argument('--wipe',
                               action = 'store_true',
                               default = False,
                               help = 'Wipe the target directory first [ False ]')
    create_parser.add_argument('--no-filters',
                               action = 'store_true',
                               default = False,
                               help = 'Ignore any include and exclude filters in the config file [ False ]')
    create_parser.add_argument('config',
                               action = 'store',
                               default = None,
                               help = 'Jail config file. [ None  ]')
  
    self._args = parser.parse_args()
    self._config = self.__load_config()
  
  def main(self):
    if self._args.command == 'create':
      return self.__command_create()
    assert False
    
  def __command_create(self):
    if not path.isfile(self._args.config):
      raise RuntimeError('File not found: %s' % (self._args.config))
    variables = {
      'root': self._args.location,
      'source_dir': path.dirname(self._args.config),
      'username': user.USERNAME,
    }
    if host.SYSTEM == host.MACOS:
      variables['DARWIN_USER_CACHE_DIR'] = execute.execute('getconf DARWIN_USER_CACHE_DIR').stdout.strip()
    cf = config_file(self._args.config, variables)
    if self._args.wipe:
      file_util.remove(self._args.location)
    jail.create(self._args.location, self._config, self._args.no_filters)
    return 0

  def __load_config(self):
    if not path.isfile(self._args.config):
      raise RuntimeError('File not found: %s' % (self._args.config))
    variables = {
      'root': self._args.location,
      'source_dir': path.dirname(self._args.config),
      'username': user.USERNAME,
    }
    if host.SYSTEM == host.MACOS:
      variables['DARWIN_USER_CACHE_DIR'] = execute.execute('getconf DARWIN_USER_CACHE_DIR').stdout.strip()
    cf = config_file(self._args.config, variables)
    return cf
  
  @classmethod
  def run(clazz):
    raise SystemExit(jail_cli().main())

if __name__ == '__main__':
  jail_cli.run()
