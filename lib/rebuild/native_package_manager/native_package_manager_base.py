#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod, ABCMeta
from collections import namedtuple
from bes.system.compat import with_metaclass

class native_package_manager_base(with_metaclass(ABCMeta, object)):

  def __init__(self):
    pass
  
  @abstractmethod
  def installed_packages(self, interface):
    'Return a list of packages on this computer.'
    pass

  @abstractmethod
  def package_files(self, package_name):
    'Return a list of installed files for the given package.'
    pass

  @abstractmethod
  def package_dirs(self, package_name):
    'Return a list of installed dirs for the given package.'
    pass

  @abstractmethod
  def package_contents(self, package_name):
    'Return a list of contents for the given package.'
    pass

  @abstractmethod
  def is_installed(self, package_name):
    'Return True if package is installed.'
    pass

  @abstractmethod
  def owner(self, filename):
    'Return the package that owns filename.'
    pass

  @abstractmethod
  def package_info(self, filename):
    'Return info structure about the package.'
    pass
  
