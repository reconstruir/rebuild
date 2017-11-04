#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import argparse, os, os.path as path, sys

try:
  from bes.common import Shell
except:
  p = path.abspath(path.normpath(path.join(path.dirname(__file__), '../../bes/lib')))
  sys.path.append(p)
  p = path.abspath(path.normpath(path.join(path.dirname(__file__), '../lib')))
  sys.path.append(p)


from bes.common import Shell
from rebuild.toolchain.darwin import darwin_sdk
from rebuild.toolchain.darwin import xcrun
from rebuild.toolchain import ar_replacement

AR_COMMAND_CONTENTS = 't'
AR_COMMAND_EXTRACT = 'x'
AR_COMMAND_QUIET = 'c'
AR_COMMAND_REPLACE = 'r'
AR_COMMAND_UPDATE = 'u'

AR_COMMANDS = set([
  AR_COMMAND_CONTENTS,
  AR_COMMAND_EXTRACT,
  AR_COMMAND_QUIET,
  AR_COMMAND_REPLACE,
  AR_COMMAND_UPDATE,
])

DEFAULT_LIPO = os.environ.get('LIPO', 'lipo')
DEFAULT_AR = os.environ.get('AR_REAL', None) or os.environ.get('AR', 'ar')
DEFAULT_LIBTOOL = os.environ.get('APPLE_LIBTOOL', 'libtool')
DEFAULT_RANLIB = os.environ.get('RANLIB', 'ranlib')

def main():
  ap = argparse.ArgumentParser()

  ap.add_argument('--replace',
                  '-r',
                  action = 'store_true',
                  default = False,
                  help = 'Archive replace. [ False ]')
  ap.add_argument('--contents',
                  '-t',
                  action = 'store_true',
                  default = False,
                  help = 'Archive contents. [ False ]')
  ap.add_argument('--extract',
                  '-x',
                  action = 'store_true',
                  default = False,
                  help = 'Archive extract. [ False ]')
  ap.add_argument('--quiet',
                  '-c',
                  action = 'store_true',
                  default = False,
                  help = 'Quiet mode. [ False ]')
  ap.add_argument('--update',
                  '-u',
                  action = 'store_true',
                  default = False,
                  help = 'Archive update. [ False ]')
  ap.add_argument('--sdk',
                  action = 'store',
                  default = None,
                  help = 'IOS xcode sdk to use to find ar, lipo and libtool. [ None ]')
  ap.add_argument('--ar',
                  action = 'store',
                  default = DEFAULT_AR,
                  help = 'Path to ar executable. [ %s ]' % (DEFAULT_AR))
  ap.add_argument('--lipo',
                  action = 'store',
                  default = DEFAULT_LIPO,
                  help = 'Path to lipo executable. [ %s ]' % (DEFAULT_LIPO))
  ap.add_argument('--libtool',
                  action = 'store',
                  default = DEFAULT_LIBTOOL,
                  help = 'Path to libtool executable. [ %s ]' % (DEFAULT_LIBTOOL))
  ap.add_argument('--ranlib',
                  action = 'store',
                  default = DEFAULT_RANLIB,
                  help = 'Path to ranlib executable. [ %s ]' % (DEFAULT_RANLIB))
  ap.add_argument('rest', action = 'store', nargs = '+', help = 'Rest of AR args')

  args = ap.parse_args()

  ar_commands = None
  if len(args.rest) > 0 and _is_ar_command(args.rest[0]):
    ar_commands = args.rest.pop(0)

  if ar_commands:
    _update_ar_commands(ar_commands, args)

  ar_commands_count = _count_ar_commands(args)

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
    _command_replace(archive, objects, tools)
  elif args.extract:
    if objects:
      raise RuntimeError('Too many arguments for extract: %s' % (' '.join(objects)))
    _command_extract(archive, tools)
  elif args.contents:
#    if objects:
#      raise RuntimeError('Too many arguments for extract: %s' % (' '.join(objects)))
    _command_contents(archive, tools)
  
  return 0

def _is_ar_command(s):
  'Return True if s is an ar command.'
  return False not in [ c in AR_COMMANDS for c in s ]

def _update_ar_commands(ar_commands, args):
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

def _count_ar_commands(args):
  count = 0
  if args.contents:
    count += 1
  if args.extract:
    count += 1
  if args.replace:
    count += 1
  return count

def _command_replace(archive, objects, tools):
  ar_replacement.replace(archive, objects, tools = tools)
  
def _command_extract(archive, tools):
  ar_replacement.extract(archive, os.getcwd(), tools = tools)

def _command_contents(archive, tools):
  contents = ar_replacement.contents(archive, tools = tools)
  for c in contents:
    print(c)
  
if __name__ == '__main__':
  raise SystemExit(main())
