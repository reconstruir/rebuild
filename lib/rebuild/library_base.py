#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class library_base(with_metaclass(ABCMeta, object)):

  def __init__(self):
    pass
  
  @abstractmethod
  def is_shared_library(self, filename):
    'Return True if filename is a shared library.'
    pass

  @abstractmethod
  def is_static_library(self, filename):
    'Return True if filename is a shared library.'
    pass

  @abstractmethod
  def dependencies(self, filename):
    'Return a list of dependencies for filename (executable or shared lib) or None if not applicable.'
    pass

  @abstractmethod
  def shared_extension(self):
    'Return the shared library extension.'
    pass

  @abstractmethod
  def static_extension(self):
    'Return the static library extension.'
    pass

  @abstractmethod
  def shared_prefix(self):
    'Return the shared library prefix.'
    pass

  @abstractmethod
  def static_prefix(self):
    'Return the static library prefix.'
    pass
