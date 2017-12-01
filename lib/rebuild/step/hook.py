#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import ABCMeta
import os.path as path
from bes.system.compat import with_metaclass
from bes.common import object_util, string_list, string_util
from bes.python import code
from rebuild.dependency import dependency_provider
from .hook_registry import hook_registry

class hook_register_meta(ABCMeta):

  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    hook_registry.register_hook_class(clazz)
    return clazz

class hook(with_metaclass(hook_register_meta, dependency_provider)):

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
    if not string_util.is_string(s):
      raise RuntimeError('Invalid hook: \"%s\"' % (s))
    v = s.partition(':')
    if not v[1] == ':':
      raise RuntimeError('Invalid hook: \"%s\"' % (s))
    filename = v[0].strip()
    function_name = v[2].strip()
    return hook(filename, function_name)

  @classmethod
  def parse_list(clazz, l):
    'Parse a list of hooks from a list of strings.'
    if not string_list.is_string_list(l):
      raise RuntimeError('Not a string list: \"%s\"' % (str(l)))
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
  def is_hook(clazz, o):
    return isinstance(o, hook)

  @classmethod
  def is_hook_list(clazz, l):
    return object_util.is_homogeneous(l, hook)

  @classmethod
  def hook_list_filenames(clazz, l):
    assert clazz.is_hook_list(l)
    return [ h.filename for h in l ]
