#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import ABCMeta, abstractmethod
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
    self.filename = filename

  def provided(self):
    'Return a list of dependencies provided by this provider.'
    return [ self.filename ]
    
  @abstractmethod
  def execute(self, script, env, args):
    'Execute the step.'
    pass

  @classmethod
  def load(self, filename):
    'Load a hook dynamically.'
    pass
