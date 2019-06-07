#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from .toolchain import toolchain
from bes.fs.file_util import file_util
from bes.common.object_util import object_util
from bes.common.variable import variable
from bes.system.execute import execute

from collections import namedtuple

class compiler(object):

  DEBUG = False
  #DEBUG = True
  
  def __init__(self, build_target):
    self.build_target = build_target
    self.toolchain = toolchain.get_toolchain(self.build_target)
    self.variables = {}
    self.variables.update(self.toolchain.compiler_environment())
    self.variables.update(self.toolchain.compiler_flags_flat())

  _target = namedtuple('_target', 'source, object')
  def compile_c(self, sources, objects = None, cflags = None):
    assert sources
    cflags = cflags or []
    sources = object_util.listify(sources)
    if objects:
      objects = object_util.listify(objects)
    targets = self._make_targets(sources, objects)

    for src, obj in targets:
      cmd = '$CC $CFLAGS %s -c $(SRC) -o $(OBJ)' % (' '.join(cflags))
      variables = copy.deepcopy(self.variables)
      variables['SRC'] = src
      variables['OBJ'] = obj
      cmd = variable.substitute(cmd, variables)
      print(cmd)
      self._execute_cmd(cmd)
    return targets

  def link_exe(self, exe, objects, ldflags = None):
    assert objects
    ldflags = ldflags or []
    objects = object_util.listify(objects)
    cmd = '$CC %s -o %s $LDFLAGS %s' % (' '.join(objects), exe, ' '.join(ldflags))
    cmd = variable.substitute(cmd, self.variables)
    self._execute_cmd(cmd)
    return exe
  
  def make_static_lib(self, lib, objects, arflags = None):
    assert objects
    objects = object_util.listify(objects)
    cmd = '$AR $AR_FLAGS %s %s' % (lib, ' '.join(objects))
    cmd = variable.substitute(cmd, self.variables)
    self._execute_cmd(cmd)
    return lib

  def make_shared_lib(self, lib, objects, ldflags = None):
    assert objects
    ldflags = ldflags or []
    objects = object_util.listify(objects)
    cmd = '$CC -shared $LDFLAGS %s %s -o %s' % (' '.join(ldflags), ' '.join(objects), lib)
    cmd = variable.substitute(cmd, self.variables)
    self._execute_cmd(cmd)
    return lib
  
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
    return [ clazz._target(*x) for x in zip(sources, objects) ]
    
  @classmethod
  def _make_object_filename(clazz, source):
    return file_util.remove_extension(source) + '.o'
  
  @classmethod
  def _execute_cmd(clazz, cmd):
    if clazz.DEBUG:
      print('COMPILER CMD: %s' % (cmd))
    return execute.execute(cmd)
