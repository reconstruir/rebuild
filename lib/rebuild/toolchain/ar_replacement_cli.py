#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path, sys

#import argparse, copy, os, os.path as path
#from rem_health.lab_results import results_finder, results_parser
#from bes.common import algorithm, check, table
#from bes.text import text_table, text_cell_renderer
#from rem_health.pdf import parse as pdf_parse

class ar_replacement_cli(object):
  
  def __init__(self):
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument('--replace',
                             '-r',
                             action = 'store_true',
                             default = False,
                             help = 'Archive replace. [ False ]')
    self.parser.add_argument('--contents',
                             '-t',
                             action = 'store_true',
                             default = False,
                             help = 'Archive contents. [ False ]')
    self.parser.add_argument('--extract',
                             '-x',
                             action = 'store_true',
                             default = False,
                             help = 'Archive extract. [ False ]')
    self.parser.add_argument('--quiet',
                             '-c',
                             action = 'store_true',
                             default = False,
                             help = 'Quiet mode. [ False ]')
    self.parser.add_argument('--update',
                             '-u',
                             action = 'store_true',
                             default = False,
                             help = 'Archive update. [ False ]')
    self.parser.add_argument('--sdk',
                             action = 'store',
                             default = None,
                             help = 'IOS xcode sdk to use to find ar, lipo and libtool. [ None ]')
    self.parser.add_argument('--ar',
                             action = 'store',
                             default = DEFAULT_AR,
                             help = 'Path to ar executable. [ %s ]' % (DEFAULT_AR))
    self.parser.add_argument('--lipo',
                             action = 'store',
                             default = DEFAULT_LIPO,
                             help = 'Path to lipo executable. [ %s ]' % (DEFAULT_LIPO))
    self.parser.add_argument('--libtool',
                             action = 'store',
                             default = DEFAULT_LIBTOOL,
                             help = 'Path to libtool executable. [ %s ]' % (DEFAULT_LIBTOOL))
    self.parser.add_argument('--ranlib',
                             action = 'store',
                             default = DEFAULT_RANLIB,
                             help = 'Path to ranlib executable. [ %s ]' % (DEFAULT_RANLIB))
    self.parser.add_argument('rest', action = 'store', nargs = '+', help = 'Rest of AR args')

  def main(self):
    args = self.parser.parse_args()

    ar_commands = None
    if len(args.rest) > 0 and self._is_ar_command(args.rest[0]):
      ar_commands = args.rest.pop(0)

    if ar_commands:
      self._update_ar_commands(ar_commands, args)

    ar_commands_count = self._count_ar_commands(args)

    if ar_commands_count > 1:
      raise RuntimeError('More than only mutually exclusive ar command (contents, extract, replace) selected.')

    if ar_commands_count == 0:
      args.replace = True

    if len(args.rest) == 0:
      raise RuntimeError('No argments given.')

    archive = args.rest.pop(0)
    if archive == 'unknown':
      archive = args.rest.pop(0)
    objects = args.rest

    if args.sdk:
      if not darwin_sdk.is_valid_sdk(args.sdk):
        raise RuntimeError('Invalid sdk \"%s\".  Should be one of: %s' % (sdk, ' '.join(darwin_sdk.VALID_SDKS)))
      tools = ar_replacement.Tools(xcrun.find_tool(args.sdk, 'ar'),
                                   xcrun.find_tool(args.sdk, 'libtool'),
                                   xcrun.find_tool(args.sdk, 'lipo'),
                                   xcrun.find_tool(args.sdk, 'ranlib'))
    else:
      tools = ar_replacement.Tools(args.ar, args.libtool, args.lipo, args.ranlib)

    if args.replace:
      self._command_replace(archive, objects, tools)
    elif args.extract:
      if objects:
        raise RuntimeError('Too many arguments for extract: %s' % (' '.join(objects)))
      self._command_extract(archive, tools)
    elif args.contents:
#      if objects:
#        raise RuntimeError('Too many arguments for extract: %s' % (' '.join(objects)))
      self._command_contents(archive, tools)
  
    return 0

  @classmethod
  def _is_ar_command(clazz, s):
    'Return True if s is an ar command.'
    return False not in [ c in AR_COMMANDS for c in s ]

  def _update_ar_commands(self, ar_commands, args):
    for c in ar_commands:
      if c == AR_COMMAND_CONTENTS:
        args.contents = True
      elif c == AR_COMMAND_EXTRACT:
        args.extract = True
      elif c == AR_COMMAND_QUIET:
        args.quiet = True
      elif c == AR_COMMAND_REPLACE:
        args.replace = True
      elif c == AR_COMMAND_UPDATE:
        args.update = True

  @classmethod
  def _count_ar_commands(self, args):
    count = 0
    if args.contents:
      count += 1
    if args.extract:
      count += 1
    if args.replace:
      count += 1
    return count

  def _command_replace(self, archive, objects, tools):
    ar_replacement.replace(archive, objects, tools = tools)
  
  def _command_extract(self, archive, tools):
    ar_replacement.extract(archive, os.getcwd(), tools = tools)

  def _command_contents(self, archive, tools):
    contents = ar_replacement.contents(archive, tools = tools)
    for c in contents:
      print(c)
  
  @classmethod
  def run(clazz):
    raise SystemExit(ar_replacement_cli().main())
