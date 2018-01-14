#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from .package import package

class package_list(object):

  @classmethod
  def sort_by_descriptor(clazz, packages):
    'Sort a list of packages in ascending order using package info.'
    check.check_package_seq(packages)
    return sorted(packages, key = lambda package: package.info)

  @classmethod
  def latest_versions(clazz, packages):
    'Return a list of only the lastest version of any package with multiple versions.'
    check.check_package_seq(packages)
    packages = clazz.sort_by_descriptor(packages)
    d = {}
    for package in packages:
      d[package.info.name] = package
    return clazz.sort_by_descriptor(d.values())

  @classmethod
  def descriptors(clazz, packages):
    'Return a list of descriptors for the given list of packages.'
    check.check_package_seq(packages)
    return [ package.info for package in packages ]
