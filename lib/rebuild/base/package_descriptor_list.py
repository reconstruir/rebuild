#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from .package_descriptor import package_descriptor

class package_descriptor_list(object):

  @classmethod
  def dependency_map(clazz, descriptors):
    'Return a map of dependencies for the given descriptor list.'
    check.check_package_descriptor_seq(descriptors)
    dep_map = {}
    for pd in descriptors:
      if pd.name in dep_map:
        raise RuntimeError('already in dependency map: %s' % (pd.name))
      dep_map[pd.name] = pd.requirements_names | pd.build_requirements_names
    return dep_map

  @classmethod
  def descriptor_map(clazz, descriptors):
    'Return a map for the given descriptor list.'
    check.check_package_descriptor_seq(descriptors)
    desc_map = {}
    for pd in descriptors:
      if pd.name in desc_map:
        raise RuntimeError('already in descriptor map: %s' % (pd.name))
      desc_map[pd.name] = pd
    return desc_map

  @classmethod
  def sort_by_name(clazz, descriptors):
    'Sort a list of descriptors in ascending order using package info.'
    check.check_package_descriptor_seq(descriptors)
    return sorted(descriptors, cmp = package_descriptor.full_name_cmp)

  @classmethod
  def latest_versions(clazz, descriptors):
    'Return a list of only the lastest version of any package with multiple versions.'
    check.check_package_descriptor_seq(descriptors)
    descriptors = clazz.sort_by_full_name(descriptors)
    d = {}
    for package in descriptors:
      d[package.info.name] = package
    return clazz.sort_by_descriptor(d.values())

  @classmethod
  def filter_out_by_name(clazz, descriptors, name):
    'Return a list of only the descriptors that dont match name.'
    check.check_package_descriptor_seq(descriptors)
    return [ pd for pd in descriptors if pd.name != name ]
