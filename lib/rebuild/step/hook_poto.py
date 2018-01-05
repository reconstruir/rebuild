#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, object_util, string_util
from bes.python import code
from rebuild.dependency import dependency_provider

class hook_poto(dependency_provider):

  def __init__(self, filename, function_name):
    'Create a new hook.'
    self._filename = filename
    self._function_name = function_name
    self._root_dir = None
    self._function = None

  def provided(self):
    'Return a list of dependencies provided by this provider.'
    return [ self.filename ]
    
  def __str__(self):
    return '%s:%s' % (self.filename, self.function_name)

  def __eq__(self, other):
    return self.filename == other.filename and self.function_name == other.function_name

  @property
  def filename(self):
    if self._root_dir:
      return path.join(self._root_dir, self._filename)
    else:
      return self._filename
    
  @filename.setter
  def filename(self, unused):
    raise RuntimeError('filename is immutable')
  
  @property
  def function_name(self):
    #raise RuntimeError('filename is private')
    return self._function_name
    
  @function_name.setter
  def function_name(self, unused):
    raise RuntimeError('function_name is immutable')

  @property
  def root_dir(self):
    raise RuntimeError('root_dir is private')

  @root_dir.setter
  def root_dir(self, root_dir):
    if self._root_dir != None:
      raise RuntimeError('root_dir can only be set once')
    self._root_dir = path.normpath(root_dir)

  @classmethod
  def parse(clazz, s):
    'Parse a hook from a string.'
    if not check.is_string(s):
      raise RuntimeError('Invalid hook: \"%s\"' % (s))
    v = s.partition(':')
    if not v[1] == ':':
      raise RuntimeError('Invalid hook: \"%s\"' % (s))
    filename = v[0].strip()
    function_name = v[2].strip()
    return clazz(filename, function_name)

  @classmethod
  def parse_list(clazz, l):
    'Parse a list of hooks from a list of strings.'
    check.check_string_seq(l, 'l')
    return [ clazz.parse(s) for s in l ]
    
  def _load(self, extra_code = None):
    filename = self.filename
    if not path.isfile(filename):
      raise RuntimeError('hook file not found: %s' % (filename))
    tmp_globals = {}
    tmp_locals = {}
    if extra_code:
      exec(extra_code, tmp_locals, tmp_globals)
    code.execfile(filename, tmp_globals, tmp_locals)
    if not self._function_name in tmp_locals:
      raise RuntimeError('function not found in %s: %s' % (filename, self._function_name))
    function = tmp_locals[self._function_name]
    if not callable(function):
      raise RuntimeError('not callable in %s: %s' % (filename, self._function_name))
    return function

  def execute(self, script, env, args, extra_code = None):
    if not self._function:
      self._function = self._load(extra_code = extra_code)
    return self._function(script, env, args)

  @classmethod
  def hook_list_filenames(clazz, hooks):
    check.check_hook_poto_seq(hooks, 'hooks')
    return [ hook.filename for hook in hooks ]

check.register_class(hook_poto)

