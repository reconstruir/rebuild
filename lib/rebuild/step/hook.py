#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import ABCMeta, abstractmethod
from bes.system.compat import with_metaclass
from bes.common import check_type
from rebuild.dependency import dependency_provider
from .hook_registry import hook_registry

class hook_register_meta(ABCMeta):

  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    hook_registry.register_hook_class(clazz)
    return clazz

class hook(with_metaclass(hook_register_meta, dependency_provider)):

  def __init__(self): #, filename):
    'Create a new hook.'
    self._filename = None

  @property
  def name(self):
    return self.__class__.__name__
    
  @property
  def filename(self):
    if not self._filename:
      raise RuntimeError('filename not set')
    return self._filename

  @filename.setter
  def filename(self, filename):
    if self._filename:
      raise RuntimeError('filename can only be set once')
    self._filename = filename
    
  def provided(self):
    'Return a list of dependencies provided by this provider.'
    return [ self.filename ]
    
  @abstractmethod
  def execute(self, script, env, args):
    'Execute the hook.  Same semantics as step.execute.'
    pass
check_type.register_class(hook)
