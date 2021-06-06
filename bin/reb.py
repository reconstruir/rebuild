#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing
import sys
import os.path as path

if __name__ == '__main__':
  # Dont remove this.  PyInstaller on Windows breaks otherwise
  multiprocessing.freeze_support()
  sys.dont_write_bytecode = True
  sys.path.remove(path.normpath(path.dirname(__file__)))
  from rebuild.cli.rebuild_cli import rebuild_cli
  rebuild_cli.run()
