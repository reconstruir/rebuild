#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path, sys

from bes.system import execute

from rebuild.base import build_blurb

class CommandLineBuild(object):
  
  def __init__(self):
    pass

  @classmethod
  def main(clazz):
    exit_code, message = clazz.__main()
    if exit_code != 0:
      build_blurb.blurb('build', message)
    raise SystemExit(exit_code)

  @classmethod
  def __main(clazz):
    ap = argparse.ArgumentParser(description = 'My hacky little build system.')

    ap.add_argument('-c', '--clean', dest = 'clean', action = 'store_true')
    ap.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true')
    ap.add_argument('-C', '--chdir', dest = 'chdir', action = 'store', default = None)

    ap.set_defaults(clean = False, verbose = False)

    ap.add_argument('scons_args', action = 'append', nargs = argparse.REMAINDER)

    args = ap.parse_args()

    if args.chdir != None:
      if not path.isdir(args.chdir):
        return ( 1, 'Not a directory: %s' % (args.chdir) )
      else:
        os.chdir(args.chdir)
  
    scons_args = args.scons_args #[0]

    if args.clean:
      cmd = clazz.make_scons_cmd(args.verbose, [ '-c' ])
      execute.execute(cmd, non_blocking = True)

    cmd = clazz.make_scons_cmd(args.verbose, scons_args)

    execute.execute(cmd, non_blocking = True)

    return ( 0, None )

  @classmethod
  def make_scons_cmd(clazz, verbose, args):
    assert isinstance(args, list)
    cmd = [ 'scons' ]
    if not verbose:
      cmd.append('-Q')
    for arg in args:
      if isinstance(arg, list):
        cmd.extend(arg)
      else:
        cmd.append(arg)
    return cmd
