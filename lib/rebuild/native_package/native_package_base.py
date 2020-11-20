#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from collections import namedtuple

from bes.common.check import check
from bes.script.blurber import blurber
from bes.system.compat import with_metaclass

class native_package_base(with_metaclass(ABCMeta, object)):

  def __init__(self, bl):
    bl = bl or blurber()
    check.check_blurber(bl)
    self._blurber = bl

  @abstractmethod
  def installed_packages(self):
    'Return a list of packages on this computer.'
    raise NotImplemented('installed_packages')

  @abstractmethod
  def package_files(self, package_name):
    'Return a list of files installed for package.'
    raise NotImplemented('package_files')

  @abstractmethod
  def package_dirs(self, package_name):
    'Return a list of dirs installed for package.'
    raise NotImplemented('package_dirs')

  @abstractmethod
  def is_installed(self, package_name):
    'Return True if package is installed.'
    raise NotImplemented('is_installed')

  @abstractmethod
  def owner(self, filename):
    'Return the package that owns filename.'
    raise NotImplemented('owner')

  @abstractmethod
  def package_info(self, filename):
    'Return info structure about the package.'
    raise NotImplemented('package_info')
  
  @abstractmethod
  def remove(self, package_name, force_package_root):
    'Remove a package.'
    raise NotImplemented('remove')

  @abstractmethod
  def install(self, package_filename):
    'Install a package.'
    raise NotImplemented('install')

  def has_package(self, package_name):
    'Return True if package_name is installed.'
    check.check_string(package_name)

    return package_name in self.installed_packages()

  def has_any_package(self, package_names):
    'Return True if any of package_names is installed.'
    check.check_string_seq(package_names)
    
    for package_name in package_names:
      if self.has_package(package_name):
        return True
    return False
