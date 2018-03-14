#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

try:
  from bes.system import execute
except Exception as ex:
  import os.path as path, sys
  p = path.abspath(path.normpath(path.join(path.dirname(__file__), '../../bes/lib')))
  sys.path.append(p)
  p = path.abspath(path.normpath(path.join(path.dirname(__file__), '../lib')))
  sys.path.append(p)

from rebuild.toolchain import ar_replacement_cli

if __name__ == '__main__':
  ar_replacement_cli.run()
