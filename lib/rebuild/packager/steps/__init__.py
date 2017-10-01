#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# Find any files in this directory that match the pattern step_*.py and import
# everything from it
import glob, os.path as path
_this_dir = path.dirname(__file__)
_step_files = glob.glob('%s/step_*.py' % (_this_dir))
_step_files = [ path.basename(f) for f in _step_files ]
_step_modules = [ f[0:-3] for f in _step_files ]
for mod in _step_modules:
  _code = 'from .%s import *' % (mod)
  exec(_code)
