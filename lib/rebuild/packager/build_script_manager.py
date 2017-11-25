#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import dict_util
from rebuild.base import build_blurb, package_descriptor, requirement
from rebuild.dependency import dependency_resolver, missing_dependency_error
from collections import namedtuple
from .build_recipe_loader import build_recipe_loader
from .build_script import build_script

class build_script_manager(object):

  def __init__(self, filenames, env):
    # Load all the scripts
    self.scripts = {}
    for filename in filenames:
      build_blurb.blurb_verbose('build', 'loading %s' % (filename))
      build_scripts = self._load_scripts(filename, env)
      for script in build_scripts:
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
        all_requirements = script.descriptor.requirements + script.descriptor.build_requirements
        all_requirements_system_resolved = requirement.resolve_requirements(all_requirements, env.config.build_target.system)

        all_requirements_dependencies_resolved = self._resolve_and_order_dependencies(all_requirements_system_resolved,
                                                                                       self.scripts, dependency_map)

        resolved_requirements = [ req for req in all_requirements_dependencies_resolved if not req.is_tool() ]
        resolved_build_requirements = [ req for req in all_requirements_dependencies_resolved if req.is_tool() ]

        assert package_descriptor.is_package_info_list(resolved_requirements)
        assert package_descriptor.is_package_info_list(resolved_build_requirements)

        script.descriptor.resolved_requirements = resolved_requirements
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
      build_requirements_names = script.descriptor.build_requirements_names_for_system(system)
      dep_map[name] = requirements_names | build_requirements_names
    return dep_map

  def subset(self, package_names):
    'Return a subset of all scripts for package_names.'
    return dict_util.filter_with_keys(self.scripts, package_names)

  def package_names(self):
    'Return all the package names.'
    return sorted(self.scripts.keys())

  def package_is_tool(self, package_name):
    'Return True if package_name is a tool.'
    return self.scripts[package_name].descriptor.is_tool()

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
    recipes = build_recipe_loader.load(filename)
    scripts = [ build_script(recipe, env.config.build_target, env) for recipe in recipes ]
    return scripts
