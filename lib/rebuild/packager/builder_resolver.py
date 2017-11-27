#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import copy, fnmatch, os, os.path as path
#from bes.common import algorithm, dict_util, object_util
#from bes.thread import thread_pool
#from bes.fs import dir_util, file_util
#from collections import namedtuple
#from rebuild.step import step_aborted
#
#from rebuild.base import build_target

from bes.common import check_type

class builder_resolver(object):

  def __init__(self, script_manager):
    self.script_manager = script_manager
    
  def resolve_packages(self, names, build_target):
    check_type.check_string_list(names)
    check_type.build_target(build_target)
    return self.script_manager.resolve_requirements(names, build_target.system)

  def package_names(self):
    return self.script_manager.package_names()

  def dependency_map(clazz, system):
    'Return a map of requirements dependencies.  A dictionary keyed on name pointing  to a set of dependencies.'
    assert isinstance(scripts, dict)
    dep_map = {}
    for name in sorted(scripts.keys()):
      script = scripts[name]
      requirements_names = script.descriptor.requirements_names_for_system(system)
      build_requirements_names = script.descriptor.build_requirements_names_for_system(system)
      dep_map[name] = requirements_names | build_requirements_names
    return dep_map
