#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
from .artifact_db import artifact_db
from bes.text import text_table

class artifact_cli(object):

  DEFAULT_DB = 'BUILD/artifacts/artifacts.db'
  
  def __init__(self):
    self.parser = argparse.ArgumentParser()
    subparsers = self.parser.add_subparsers(help = 'commands', dest = 'command')

    # query
    db_parser = subparsers.add_parser('query', help = 'Query the artifacts db')
    db_parser.add_argument('--db', action = 'store', default = self.DEFAULT_DB, help = 'The artifacts db')
    db_parser.add_argument('--metadata', '-m', action = 'store_true', help = 'Load metadata')
    db_parser.add_argument('--descriptor', '-d', action = 'store_true', help = 'Load descriptors')

  def main(self):
    args = self.parser.parse_args()
    if args.command == 'query':
      return self._command_query(args.db, args.metadata, args.descriptor)
    else:
      raise RuntimeError('Unknown command: %s' % (args.command))
    return 0

  def _command_query(self, db_filename, metadata, descriptor):
    db = artifact_db(db_filename)
    if descriptor:
      available = db.list_all_by_descriptor()
      tt = text_table(data = available)
      tt.set_labels(tuple([ f.upper() for f in available[0]._fields ]))
      print(tt)
  
    if metadata:
      available = db.list_all_by_metadata()
      data = [ a.artifact_descriptor for a in available ]
      tt = text_table(data = data)
      tt.set_labels(tuple([ f.upper() for f in available[0].artifact_descriptor._fields ]))
      print(tt)
    
  @classmethod
  def run(clazz):
    raise SystemExit(artifact_cli().main())
