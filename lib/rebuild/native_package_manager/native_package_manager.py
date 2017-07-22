#!/usr/bin/env python
#-*- coding:utf-8 -*-

from native_package_manager_base import native_package_manager_base
from bes.system import impl_loader

class native_package_manager(native_package_manager_base):
  'Top level class for dealing with system native_package_managers.'

  __impl = impl_loader.load(__file__, 'native_package_manager')

  @classmethod
  def installed_packages(clazz):
    'Return a list of installed pacakge.'
    return clazz.__impl.installed_packages()
  
  @classmethod
  def package_files(clazz, native_package_manager_name):
    'Return a list of installed files for the given package.'
    return clazz.__impl.package_files(native_package_manager_name)

  @classmethod
  def package_dirs(clazz, native_package_manager_name):
    'Return a list of installed dirs for the given package.'
    return clazz.__impl.package_dirs(native_package_manager_name)

  @classmethod
  def package_contents(clazz, native_package_manager_name):
    'Return a list of installed files for the given package.'
    return clazz.__impl.package_contents(native_package_manager_name)

  @classmethod
  def is_installed(clazz, native_package_manager_name):
    'Return True if native_package_manager is installed.'
    return clazz.__impl.is_installed(native_package_manager_name)

  @classmethod
  def owner(clazz, filename):
    'Return the package that owns filename.'
    return clazz.__impl.owner(filename)

  @classmethod
  def package_info(clazz, filename):
    'Return the package that owns filename.'
    return clazz.__impl.package_info(filename)
