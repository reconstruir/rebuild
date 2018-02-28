#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from .toolchain import toolchain
from bes.fs import file_util
from bes.common import object_util, variable
from bes.system import execute

class compiler(object):

  def __init__(self, build_target):
    self.build_target = build_target
    self.toolchain = toolchain.get_toolchain(self.build_target)

  def compile_c(self, sources, objects = None, cflags = None):
    assert sources
    sources = object_util.listify(sources)
    if objects:
      objects = object_util.listify(objects)
    targets = self._make_targets(sources, objects)

    for src, obj in targets:
      cmd = '$CC $CFLAGS -c $(SRC) -o $(OBJ)'
      variables = {}
      variables.update(self.toolchain.compiler_environment())
      variables.update(self.toolchain.compiler_flags_flat())
      variables['SRC'] = src
      variables['OBJ'] = obj
      cmd = variable.substitute(cmd, variables)
      print('CMD: %s' % (cmd))
      execute.execute(cmd)
    return targets
  
  @classmethod
  def _make_targets(clazz, sources, objects):
    assert sources
    if sources and objects:
      if len(source) != len(objects):
        raise RuntimeError('sources and objects need to have the same number of items.')
    if not objects:
      objects = [ clazz._make_object_filename(s) for s in sources ]
    sources = [ path.abspath(s) for s in sources ]
    objects = [ path.abspath(o) for o in objects ]
    return [ x for x in zip(sources, objects) ]
    
  @classmethod
  def _make_object_filename(clazz, source):
    return file_util.remove_extension(source) + '.o'
