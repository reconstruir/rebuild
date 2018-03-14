#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pkgutil, sys
_steps_path = sys.modules['rebuild.builder.steps'].__path__
for _, modname, _ in pkgutil.iter_modules(path = _steps_path):
  _source = 'from .%s import *' % (modname)
  _code = compile(_source, __file__, 'exec')
  exec(_code, globals(), locals())
