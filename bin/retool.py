#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.cli.retool_cli import retool_cli

if __name__ == '__main__':
  from os import path
  import sys
  sys.dont_write_bytecode = True
  script_name = path.basename(sys.argv[0])
  if 'rebuilder' in script_name:
    from rebuild.builder import builder_cli
    builder_cli.run()
  elif 'revenv' in script_name:
    from rebuild.venv.venv_cli import venv_cli
    venv_cli.run()
  else:
    retool_cli.run()
