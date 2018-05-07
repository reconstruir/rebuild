#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, type_checked_list
from rebuild.base import package_descriptor_list
from .package import package

class package_list(type_checked_list):

  __value_type__ = package
  
  def __init__(self, values = None):
    super(package_list, self).__init__(values = values)

  def sort_by_descriptor(self):
    self._values = sorted(self._values, key = lambda package: package.package_descriptor)
    
  def descriptors(self):
    'Return the names for all the descriptors.'
    return package_descriptor_list([ p.descriptor for p in self ])

  def latest_versions(self):
    'Return a list of only the lastest version of any package with multiple versions.'
    latest = {}
    for package in self:
      name = package.metadata.name
      if not name in latest:
        latest[name] = package
      else:
        if package.metadata.build_version > latest[name].metadata.build_version:
          latest[name] = package
    result = package_list(latest.values())
    result.sort_by_descriptor()
    return result
  
check.register_class(package_list, include_seq = False)
