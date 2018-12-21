#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
from bes.key_value import key_value_list
from bes.unix import terminal
from bes.compat import StringIO
from bes.text import text_fit

from .package import package
from .package_manager import package_manager

class package_cli(object):

  def __init__(self):
    self.parser = argparse.ArgumentParser()
    self.commands_subparser = self.parser.add_subparsers(help = 'commands',
                                                         dest = 'command')
    # file:
    self.file_parser = self.commands_subparser.add_parser('file', help = 'File')
    self.file_subparsers = self.file_parser.add_subparsers(help = 'file commands', dest = 'subcommand')

    # file:metadata
    metadata_parser = self.file_subparsers.add_parser('metadata', help = 'Metadata tools')
    metadata_parser.add_argument('filename', action = 'store', help = 'The archive')
    metadata_parser.add_argument('--raw', '-r', action = 'store_true', help = 'Print the raw metadata')
    metadata_parser.add_argument('--checksums', '-c', action = 'store_true', help = 'Print file checksums')

    # db:
    self.db_parser = self.commands_subparser.add_parser('db', help = 'Db')
    self.db_subparsers = self.db_parser.add_subparsers(help = 'db commands', dest = 'subcommand')

    # db:print
    print_parser = self.db_subparsers.add_parser('print', help = 'DB tools')
    print_parser.add_argument('filename', action = 'store', help = 'The db filename')

  def main(self):
    args = self.parser.parse_args()
    subcommand = getattr(args, 'subcommand', None)
    if subcommand:
      args.command = '%s:%s' % (args.command, subcommand)

    if args.command == 'file:metadata':
      return self._command_file_metadata(args.filename, args.raw, args.checksums)
    elif args.command == 'db:print':
      return self._command_db_print(args.filename)
    else:
      raise RuntimeError('Unknown command: %s' % (args.command))
    return 0

  def _command_file_metadata(self, filename, raw, checksums):
    p = package(filename)
    if raw:
      print(p.raw_metadata)
    else:
      d = p.metadata.to_simple_dict()
      manifest = d['manifest']
      del d['_format_version']
      d['arch'] = ' '.join(d['arch'])
      d['properties'] = str(key_value_list.from_dict(d['properties']))
      d['requirements'] = '\n              '.join(d['requirements'])
      def _i(f):
        if checksums:
          return ' '.join(f)
        else:
          return f[0]
      d['manifest'] = self.fit_stuff('manifest', ' '.join([ _i(f) for f in manifest['files'] ]))
      d['env_files'] = self.fit_stuff('env_files', ' '.join([ _i(f) for f in manifest['env_files'] ]))
      d['contents_checksum'] = manifest['contents_checksum']
      for key, value in sorted(d.items()):
        if key in [ 'files', 'env_files' ]:
          print(value)
        else:
          print('%20s: %s' % (key, value))
    return 0

  @classmethod
  def justified_label(clazz, label):
    return label.rjust(20)
  
  @classmethod
  def fit_stuff(clazz, label, message):
    buf = StringIO()
    justified_label = clazz.justified_label(label)
    delimiter = ': '
    left_width = len(justified_label) + len(delimiter)
    buf.write(justified_label)
    buf.write(delimiter)
    lines = []
    if True:
      terminal_width = terminal.width()
      width = terminal_width - left_width
      if len(message) > width:
        lines = text_fit.fit_text(message, width)
    if lines:
      first = True
      for line in lines:
        if not first:
          buf.write(' ' * left_width)
        buf.write(line)
        buf.write('\n')
        first = False
    else:
      buf.write(message)
    return buf.getvalue().rstrip()

  def _command_db_print(self, filename):
    pm = package_manager(filename, None)
    for p in pm.list_all(include_version = True):
      print(str(p))
    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(package_cli().main())
