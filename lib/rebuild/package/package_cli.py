#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
from bes.key_value import key_value_list
from rebuild.package import package
from bes.unix import terminal
from bes.compat import StringIO
from bes.text import text_fit

class package_cli(object):

  def __init__(self):
    self.parser = argparse.ArgumentParser()
    subparsers = self.parser.add_subparsers(help = 'commands', dest = 'command')

    # Metadata
    metadata_parser = subparsers.add_parser('metadata', help = 'Print archive metadata')
    metadata_parser.add_argument('filename', action = 'store', help = 'The archive')
    metadata_parser.add_argument('--raw', '-r', action = 'store_true', help = 'Print the raw metadata')
    metadata_parser.add_argument('--checksums', '-c', action = 'store_true', help = 'Print file checksums')

  def main(self):
    args = self.parser.parse_args()
    if args.command == 'metadata':
      return self._command_metadata(args.filename, args.raw, args.checksums)
    else:
      raise RuntimeError('Unknown command: %s' % (args.command))
    return 0

  def _command_metadata(self, filename, raw, checksums):
    p = package(filename)
    if raw:
      print(p.raw_metadata)
    else:
      d = p.metadata.to_simple_dict()
      files = d['files']
      del d['_format_version']
      d['arch'] = ' '.join(d['arch'])
      d['properties'] = str(key_value_list.from_dict(d['properties']))
      d['requirements'] = '\n              '.join(d['requirements'])
      def _i(f):
        if checksums:
          return ' '.join(f)
        else:
          return f[0]
      d['files'] = self.fit_stuff('files', ' '.join([ _i(f) for f in files['files'] ]))
      d['env_files'] = self.fit_stuff('env_files', ' '.join([ _i(f) for f in files['env_files'] ]))
      d['files_checksum'] = files['files_checksum']
      d['env_files_checksum'] = files['env_files_checksum']
      for key, value in sorted(d.items()):
        if key in [ 'files', 'env_files' ]:
          print(value)
        else:
          print('%20s: %s' % (key, value))
    return 0

  @classmethod
  def justified_label(clazz, label):
    return label.rjust(20) #self.__get_label_length())
  
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
  
  @classmethod
  def run(clazz):
    raise SystemExit(package_cli().main())
