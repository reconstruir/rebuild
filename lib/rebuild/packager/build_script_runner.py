#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, imp, os, os.path as path, sys

from bes.common import dict_util, object_util
from bes.fs import dir_util, file_util

from .packager import packager
from rebuild import build_blurb, build_target, package_descriptor, requirement, TarballUtil
from rebuild.dependency import dependency_resolver, missing_dependency_error
from rebuild.step_manager import Step, step_aborted, step_result

from collections import namedtuple
from .build_script import build_script

class build_script_runner(object):

  SUCCESS = 'success'
  FAILED = 'failed'
  CURRENT = 'current'
  ABORTED = 'aborted'

  RunResult = namedtuple('RunResult', 'status,packager_result')

  def __init__(self, filenames, build_target, **kargs):
    # Load all the scripts
    self.scripts = {}
    for filename in filenames:
      build_blurb.blurb_verbose('build', 'loading %s' % (filename))
      build_scripts = build_script.load_build_scripts(filename, build_target, **kargs)
      for script in build_scripts:
        self.scripts[script.package_descriptor.name] = script
        #print "filename: %s" % (script.filename)
        #print "    name: %s" % (script.name)
        #print "    requirements: %s" % (script.requirements)
        #print "    args: %s" % (script.args)
        #print ""

    dependency_map = self._dependency_map(self.scripts, build_target.system)
    
    # Resolve and order all the dependencies for all the scripts
    for name, script in sorted(self.scripts.items()):
      build_blurb.blurb_verbose('build', 'resolving dependencies for: %s - %s' % (path.relpath(script.filename), script.package_descriptor.name))
      try:
        all_requirements = script.package_descriptor.requirements + script.package_descriptor.build_requirements
        all_requirements_system_resolved = requirement.resolve_requirements(all_requirements, build_target.system)

        all_requirements_dependencies_resolved = self._resolve_and_order_dependencies(all_requirements_system_resolved,
                                                                                       self.scripts, dependency_map)

        resolved_requirements = [ req for req in all_requirements_dependencies_resolved if not req.is_tool() ]
        resolved_build_requirements = [ req for req in all_requirements_dependencies_resolved if req.is_tool() ]

        assert package_descriptor.is_package_info_list(resolved_requirements)
        assert package_descriptor.is_package_info_list(resolved_build_requirements)

        script.package_descriptor.resolved_requirements = resolved_requirements
        script.package_descriptor.resolved_build_requirements = resolved_build_requirements

      except missing_dependency_error as ex:
        raise missing_dependency_error('Missing dependency for %s: %s' % (script.filename, ' '.join(ex.missing_deps)), ex.missing_deps)
      except Exception as ex:
        print('caught unknown exception: %s' % (str(ex)))
        raise
        
  def run_build_script(self, script, env, **kargs):
    try:
      pkg = packager(script, env, self.scripts, **kargs)
      checksum_ignored = env.checksum_manager.is_ignored(script.package_descriptor.full_name)
      needs_rebuilding = checksum_ignored or script.needs_rebuilding()
      if not needs_rebuilding:
        # If the working directory is empty, it means no work happened and its useless
        if dir_util.is_empty(pkg.packager_env.working_dir):
          file_util.remove(pkg.packager_env.working_dir)
        return self.RunResult(self.CURRENT, None)
      build_blurb.blurb('build', '%s - building' % (script.package_descriptor.name))
      packager_result = pkg.execute()
      #print("CACA: packager_result: %s" % (str(packager_result)))
      if packager_result.success:
        return self.RunResult(self.SUCCESS, packager_result)
      else:
        return self.RunResult(self.FAILED, packager_result)

    except step_aborted as ex:
      return self.RunResult(self.ABORTED, None)

    assert False, 'Not Reached'
    return self.RunResult(self.FAILED, None)

  @classmethod
  def _resolve_and_order_dependencies(clazz, requirements, scripts, dependency_map):
    names = [ dep.name for dep in requirements ]
    resolved_names = dependency_resolver.resolve_deps(dependency_map, names)
    resolved = [ scripts[name].package_descriptor for name in resolved_names ]
    resolved_map = dict_util.filter_with_keys(dependency_map, resolved_names)
    build_order = dependency_resolver.build_order_flat(resolved_map)
    resolved = [ scripts[name].package_descriptor for name in build_order ]
    return resolved

  @classmethod
  def build_order_flat(clazz, scripts, system):
    'Return the build order for the given map of scripts.'
    return dependency_resolver.build_order_flat(clazz._dependency_map(scripts, system))

  @classmethod
  def build_order(clazz, scripts, system):
    'Return the build order for the given map of scripts.'
    return dependency_resolver.build_order(clazz._dependency_map(scripts, system))

  @classmethod
  def resolve_requirements(clazz, scripts, names, system):
    '''
    Return a set of resolved dependencies for the given name or names.
    Sorted alphabetically, not in build order.
    '''
    dependency_map = clazz._dependency_map(scripts, system)
    return dependency_resolver.resolve_deps(dependency_map, names)

  @classmethod
  def _dependency_map(clazz, scripts, system):
    'Return a map of requirements dependencies.  A dictionary keyed on name pointing  to a set of dependencies.'
    assert isinstance(scripts, dict)
    dep_map = {}
    for name in sorted(scripts.keys()):
      script = scripts[name]
      requirements_names = script.package_descriptor.requirements_names_for_system(system)
      build_requirements_names = script.package_descriptor.build_requirements_names_for_system(system)
      dep_map[name] = requirements_names | build_requirements_names
    return dep_map
