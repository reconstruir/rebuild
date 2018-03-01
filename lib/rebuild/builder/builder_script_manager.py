#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, dict_util
from rebuild.base import build_blurb, package_descriptor, requirement
from bes.dependency import dependency_resolver, missing_dependency_error
from collections import namedtuple
from .builder_recipe_loader import builder_recipe_loader
from .builder_script import builder_script

class builder_script_manager(object):

  def __init__(self, filenames, env):
    # Load all the scripts
    self.scripts = {}
    for filename in filenames:
      build_blurb.blurb_verbose('build', 'loading %s' % (filename))
      builder_scripts = self._load_scripts(filename, env)
      for script in builder_scripts:
        self.scripts[script.descriptor.name] = script
        #print "filename: %s" % (script.filename)
        #print "    name: %s" % (script.name)
        #print "    requirements: %s" % (script.requirements)
        #print "    args: %s" % (script.args)
        #print ""

    dependency_map = self._dependency_map(self.scripts, env.config.build_target.system)
    
    # Resolve and order all the dependencies for all the scripts
    for name, script in sorted(self.scripts.items()):
      build_blurb.blurb_verbose('build', 'resolving dependencies for: %s - %s' % (path.relpath(script.filename), script.descriptor.name))
      try:
        requirements = script.descriptor.requirements.resolve(env.config.build_target.system)
        resolved_requirements = self._resolve_and_order_dependencies(requirements,
                                                                     self.scripts, dependency_map)
        build_tool_requirements = script.descriptor.build_tool_requirements.resolve(env.config.build_target.system)
        resolved_build_tool_requirements = self._resolve_and_order_dependencies(build_tool_requirements,
                                                                                self.scripts, dependency_map)
        build_requirements = script.descriptor.build_requirements.resolve(env.config.build_target.system)
        resolved_build_requirements = self._resolve_and_order_dependencies(build_requirements,
                                                                           self.scripts, dependency_map)
        
        check.check_package_descriptor_seq(resolved_requirements)
        check.check_package_descriptor_seq(resolved_build_tool_requirements)
        check.check_package_descriptor_seq(resolved_build_requirements)

        script.descriptor.resolved_requirements = resolved_requirements
        script.descriptor.resolved_build_tool_requirements = resolved_build_tool_requirements
        script.descriptor.resolved_build_requirements = resolved_build_requirements

      except missing_dependency_error as ex:
        raise missing_dependency_error('Missing dependency for %s: %s' % (script.filename, ' '.join(ex.missing_deps)), ex.missing_deps)
      except Exception as ex:
        print('caught unknown exception: %s' % (str(ex)))
        raise

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

  @classmethod
  def build_order(clazz, scripts, system):
    'Return the build order for the given map of scripts.'
    return dependency_resolver.build_order(clazz._dependency_map(scripts, system))

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
      requirements_names = script.descriptor.requirements_names_for_system(system)
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

  _partitioned = namedtuple('_partitioned', 'libs,tools')
  def partition_libs_and_tools(self, package_names):
    'Return a subset of all scripts for package_names.'
    libs = []
    tools = []
    for package_name in package_names:
      script = self.scripts[package_name]
      if script.descriptor.is_tool():
        tools.append(package_name)
      else:
        libs.append(package_name)
    return self._partitioned(libs, tools)
        
  @classmethod
  def _load_scripts(clazz, filename, env):
    scripts = []
    recipes = builder_recipe_loader.load(filename)
    scripts = [ builder_script(recipe, env) for recipe in recipes ]
    return scripts
