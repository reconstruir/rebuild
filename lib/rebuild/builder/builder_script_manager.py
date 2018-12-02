#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, pprint
from bes.common import check, dict_util
from rebuild.base import build_blurb, package_descriptor, requirement, requirement_manager
from bes.dependency import dependency_resolver, missing_dependency_error
from collections import namedtuple
from .builder_recipe_loader import builder_recipe_loader
from .builder_script import builder_script

class builder_script_manager(object):

  def __init__(self, filenames, build_target, env):
    # Load all the scripts
    self.scripts = {}
    for filename in filenames:
      build_blurb.blurb_verbose('rebuild', 'loading %s' % (filename))
      builder_scripts = self._load_scripts(filename, build_target, env)
      for script in builder_scripts:
        #print('%s: requirements=%s' % (script.descriptor.name, str(script.descriptor.requirements)))
        self.scripts[script.descriptor.name] = script
        #print "filename: %s" % (script.filename)
        #print "    name: %s" % (script.name)
        #print "    requirements: %s" % (script.requirements)
        #print "    args: %s" % (script.args)
        #print ""

  def __getitem__(self, name):
    return self.scripts[name]

  @classmethod
  def _resolve_and_order_dependencies(clazz, requirements, scripts, dependency_map):
    names = [ dep.name for dep in requirements ]
    descriptor_map = {}
    for name, script in scripts.items():
      descriptor_map[name] = script.descriptor
    return dependency_resolver.resolve_and_order_deps(names, descriptor_map, dependency_map)

  @classmethod
  def build_order_flat(clazz, scripts, system):
    'Return the build order for the given map of scripts.'
    return dependency_resolver.build_order_flat(clazz._dependency_map(scripts, system))

  def caca_build_order(self, names, system):
    'Return the build order for the given map of scripts.'
    return dependency_resolver.build_order_flat(clazz._dependency_map(scripts, system))

  def resolve_requirements(self, names, system):
    '''
    Return a set of resolved dependencies for the given name or names.
    Sorted alphabetically, not in build order.
    '''
    dep_map = self._dependency_map(self.scripts, system)
    return dependency_resolver.resolve_deps(dep_map, names)

  @classmethod
  def _dependency_map(clazz, scripts, system):
    'Return a map of requirements dependencies.  A dictionary keyed on name pointing  to a set of dependencies.'
    assert isinstance(scripts, dict)
    dep_map = {}
    for name in sorted(scripts.keys()):
      script = scripts[name]
      requirements_names = script.descriptor.requirements._names_for_system(system)
      build_tool_requirements_names = script.descriptor.build_tool_requirements_names_for_system(system)
      build_requirements_names = script.descriptor.build_requirements_names_for_system(system)
      dep_map[name] = requirements_names | build_requirements_names | build_tool_requirements_names
    return dep_map

  def subset(self, package_names):
    'Return a subset of all scripts for package_names.'
    return dict_util.filter_with_keys(self.scripts, package_names)

  def package_names(self):
    'Return all the package names.'
    return sorted(self.scripts.keys())

  @classmethod
  def _load_scripts(clazz, filename, build_target, env):
    scripts = []
    recipes = builder_recipe_loader.load(env.recipe_load_env, filename)
    scripts = [ builder_script(recipe, build_target, env) for recipe in recipes ]
    return scripts

  def _step_values_as_dict(self):
    result = {}
    for name, script in self.scripts.items():
      result[name] = script.step_values_as_dict()
    return result

  def print_step_values(self):
    d = self._step_values_as_dict()
    for package_name, step_values in sorted(d.items()):
      for step_value in step_values:
        step_name = step_value[0]
        step_values = step_value[1]
        for key, value in step_values.items():
          if value:
            print('%s: %s: %s: %s' % (package_name, step_name, key, pprint.pformat(value)))
