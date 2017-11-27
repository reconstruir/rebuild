#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import object_util
from .package import package

class package_list(object):

  @classmethod
  def is_package_list(clazz, packages):
    return object_util.is_homogeneous(packages, package)

  @classmethod
  def sort_by_descriptor(clazz, packages):
    'Sort a list of packages in ascending order using package info.'
    assert clazz.is_package_list(packages)
    return sorted(packages, key = lambda package: package.info)

  @classmethod
  def latest_versions(clazz, packages):
    'Return a list of only the lastest version of any package with multiple versions.'
    assert clazz.is_package_list(packages)
    packages = clazz.sort_by_descriptor(packages)
    d = {}
    for package in packages:
      d[package.info.name] = package
    return clazz.sort_by_descriptor(d.values())

  @classmethod
  def descriptors(clazz, packages):
    'Return a list of descriptors for the given list of packages.'
    assert clazz.is_package_list(packages)
    return [ package.info for package in packages ]
