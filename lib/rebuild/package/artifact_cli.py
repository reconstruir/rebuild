#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
from bes.common import table
from bes.text import text_table
from rebuild.base import build_target_cli

from .artifact_db import artifact_db

class artifact_cli(build_target_cli):

  DEFAULT_DB = 'BUILD/artifacts/artifacts.db'
  
  def __init__(self):
    self.parser = argparse.ArgumentParser()
    subparsers = self.parser.add_subparsers(help = 'commands', dest = 'command')

    # query
    db_parser = subparsers.add_parser('query', help = 'Query the artifacts db')
    db_parser.add_argument('--db', action = 'store', default = self.DEFAULT_DB, help = 'The artifacts db')
    db_parser.add_argument('--metadata', '-m', action = 'store_true', help = 'Load metadata')
    db_parser.add_argument('--descriptor', '-d', action = 'store_true', help = 'Load descriptors')
    db_parser.add_argument('--name', '-n', action = 'store', default = None, help = 'Name to query')
    self.build_target_add_arguments(db_parser, True)
    
  def main(self):
    self.args = self.parser.parse_args()
    self.build_target = self.build_target_resolve(self.args)
    if self.args.command == 'query':
      return self._command_query()
    else:
      raise RuntimeError('Unknown command: %s' % (args.command))
    return 0

  def _command_query(self):
    db = artifact_db(self.args.db)
    if self.args.descriptor:
      available = db.list_all_by_descriptor()
      if self.args.name:
        available = available.filter_by_name(self.args.name)
      if self.args.level:
        available = available.filter_by_level(self.args.level)
      if self.args.system:
        available = available.filter_by_system(self.args.system)
      data = table(data = available)
      data.column_names = tuple([ f.upper() for f in available[0]._fields ])
      data.modify_column('ARCHS', lambda archs: ' '.join(archs))
      tt = text_table(data = data)
      tt.set_labels(data.column_names)
      print(tt)
  
    if self.args.metadata:
      available = db.list_all_by_metadata()
      data = [ a.artifact_descriptor for a in available ]
      tt = text_table(data = data)
      tt.set_labels(tuple([ f.upper() for f in available[0].artifact_descriptor._fields ]))
      print(tt)
    
  @classmethod
  def run(clazz):
    raise SystemExit(artifact_cli().main())
