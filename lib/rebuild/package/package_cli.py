#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
from bes.key_value import key_value_list
from rebuild.package import package

class package_cli(object):

  TOOLS = 'tools'
  UPDATE = 'update'

  DEFAULT_ROOT_DIR = path.expanduser('~/.rebuild')
  
  def __init__(self):
    self.parser = argparse.ArgumentParser()
    subparsers = self.parser.add_subparsers(help = 'commands', dest = 'command')

    # Metadata
    metadata_parser = subparsers.add_parser('metadata', help = 'Print archive metadata')
    metadata_parser.add_argument('filename', action = 'store', help = 'The archive')

  def main(self):
    args = self.parser.parse_args()
    if args.command == 'metadata':
      return self._command_metadata(args.filename)
    else:
      raise RuntimeError('Unknown command: %s' % (args.command))
    return 0

  def _command_metadata(self, filename):
    p = package(filename)
    d = p.metadata.to_simple_dict()
    d['archs'] = ' '.join(d['archs'])
    d['properties'] = str(key_value_list.from_dict(d['properties']))
    d['requirements'] = ' '.join(d['requirements'])
    d['files'] = ' '.join(d['files'])
    for key, value in sorted(d.items()):
      print('%15s: %s' % (key, value))
    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(package_cli().main())
