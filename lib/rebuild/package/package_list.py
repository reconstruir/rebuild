#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, type_checked_list
from rebuild.base import package_descriptor_list
from .package import package

class package_list(object):

  @classmethod
  def sort_by_descriptor(clazz, packages):
    'Sort a list of packages in ascending order using package info.'
    check.check_package_seq(packages)
    return sorted(packages, key = lambda package: package.descriptor)

  @classmethod
  def latest_versions(clazz, packages):
    'Return a list of only the lastest version of any package with multiple versions.'
    check.check_package_seq(packages)
    packages = clazz.sort_by_descriptor(packages)
    d = {}
    for package in packages:
      d[package.descriptor.name] = package
    return clazz.sort_by_descriptor(d.values())

  @classmethod
  def descriptors(clazz, packages):
    'Return a list of descriptors for the given list of packages.'
    check.check_package_seq(packages)
    return [ package.descriptor for package in packages ]

class xpackage_list(type_checked_list):

  def __init__(self, values = None):
    super(xpackage_list, self).__init__(package, values = values)

  def sort_by_descriptor(self):
    self._values = sorted(self._values, key = lambda package: package.descriptor)
    
  def descriptors(self):
    'Return the names for all the descriptors.'
    return package_descriptor_list([ p.descriptor for p in self ])

  def latest_versions(self):
    'Return a list of only the lastest version of any package with multiple versions.'
    latest = {}
    for package in self:
      name = package.metadata.name
      if not name in result:
        latest[name] = package
      else:
        if package.metadata.build_version > result[name].metadata.build_version:
          latest[name] = package
    result = clazz(result.values())
    result.sort_by_descriptor()
    return result
  
#check.register_class(package_list, include_seq = False)
