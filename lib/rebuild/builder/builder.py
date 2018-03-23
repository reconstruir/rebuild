#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, fnmatch, os, os.path as path
from bes.common import algorithm, dict_util, object_util
from bes.thread import thread_pool
from bes.fs import dir_util, file_util
from collections import namedtuple
from rebuild.step import step_aborted

from rebuild.base import build_blurb

class builder(object):

  REBUILD_FILENAME = 'build.py'
  
  def __init__(self, env):
    build_blurb.add_blurb(self, label = 'build')
    self._env = env
    self.thread_pool = thread_pool(1)

  def exclude(self, excluded_packages):
    excluded_packages = object_util.listify(excluded_packages)
    for excluded_package in excluded_packages:
      if excluded_package in self._env.script_manager.scripts:
        del self._env.script_manager.scripts[excluded_package]

  def __match_arg_exact(self, arg):
    if arg in self._env.script_manager.scripts:
      return arg
    for package_name, script in self._env.script_manager.scripts.items():
      if script.filename.endswith(arg):
        return package_name
      p = path.normpath(path.join(arg, self.REBUILD_FILENAME))
      if script.filename.endswith(p):
        return package_name
    return None

  def __match_arg_with_pattern(self, arg):
    result = []
    pattern = '*%s*' % (arg)
    for package_name, script in self._env.script_manager.scripts.items():
      filename = path.relpath(script.filename)
      if fnmatch.fnmatch(filename, pattern):
        result.append(package_name)
    return result

  def _resolve_arg(self, arg):
    exact_match = self.__match_arg_exact(arg)
    if exact_match:
      return [ exact_match ]
    result = self.__match_arg_with_pattern(arg)
    return result

  _resolved_args = namedtuple('_resolved_args', 'package_names,invalid_args')
  def check_and_resolve_cmd_line_args(self, args):
    'Check that each arg in the command line is valid or try to resolve it.'
    package_names = []
    invalid_args = []
    for arg in args:
      resolved_package_names = self._resolve_arg(arg)
      if resolved_package_names:
        package_names.extend(resolved_package_names)
      else:
        invalid_args.append(arg)
    return self._resolved_args(package_names, invalid_args)

  def remove_checksums(self, package_names):
    'Remove checksums for the given packages given as package names.'
    scripts = self._env.script_manager.subset(package_names)
    descriptors = [ script.descriptor for script in scripts.values() ]
    self._env.checksum_manager.remove_checksums(descriptors, self._env.config.build_target)

  def wipe_build_dirs(self, package_names):
    self.blurb('wiping build dirs for: %s' % (' '.join(package_names)), fit = True)
    for package_name in package_names:
      script = self._env.script_manager.scripts[package_name]
      builds_dir = self._env.config.builds_dir(script.build_target)
      if path.isdir(builds_dir):
        patterns = '*%s-*' % (package_name)
        tmp_dirs = dir_util.list(builds_dir, patterns = patterns)
        for tmp_dir in tmp_dirs:
          self.blurb('wiping temporary build directory: %s' % (path.relpath(tmp_dir)))
        file_util.remove(tmp_dirs)

  def scratch_existing_data(self):
    dirs_to_scratch = [ 'artifacts', 'builds', 'checksums', 'tools' ]
    dirs = [ path.join(self._env.config.build_root, d) for d in dirs_to_scratch ]
    for d in dirs:
      print('scratching existing data: %s' % (path.relpath(d)))
      file_util.remove(d)
    
  def wipe_old_build_dirs(self, package_names):
    for package_name in package_names:
      script = self._env.script_manager.scripts[package_name]
      builds_dir = self._env.config.builds_dir(script.build_target)
      if path.isdir(builds_dir):
        tmp_dirs = dir_util.older_dirs(dir_util.list(builds_dir), hours = 24)
        for tmp_dir in tmp_dirs:
          self.blurb('wiping expired tmp build directory: %s' % (path.relpath(tmp_dir)))
          file_util.remove(tmp_dir)

  EXIT_CODE_SUCCESS = 0
  EXIT_CODE_FAILED = 1
  EXIT_CODE_ABORTED = 2

  def _call_build_script(self, script):
    result = self._build_script(script, self._env)
    if result.status == self.SCRIPT_SUCCESS:
      self.blurb('%s - SUCCESS' % (script.descriptor.name))
      return self.EXIT_CODE_SUCCESS
    elif result.status == self.SCRIPT_FAILED:
      self.blurb('FAILED: %s - %s - %s' % (script.descriptor.name, result.packager_result.failed_step.__class__.__name__, result.packager_result.message))
      return self.EXIT_CODE_FAILED
    elif result.status == self.SCRIPT_CURRENT:
      self.blurb('%s - up-to-date.' % (script.descriptor.name))
      return self.EXIT_CODE_SUCCESS
    elif result.status == self.SCRIPT_ABORTED:
      self.blurb('aborted')
      return self.EXIT_CODE_ABORTED
    assert False
    return self.EXIT_CODE_FAILED

  SCRIPT_SUCCESS = 'success'
  SCRIPT_FAILED = 'failed'
  SCRIPT_CURRENT = 'current'
  SCRIPT_ABORTED = 'aborted'
  _run_result = namedtuple('_run_result', 'status,packager_result')
  
  def _build_script(self, script, env):
    try:
      checksum_ignored = env.checksum_manager.is_ignored(script.descriptor.full_name)
      needs_rebuilding = checksum_ignored or script.needs_rebuilding()
      if not needs_rebuilding:
        # If the working directory is empty, it means no work happened and its useless
        if path.exists(script.working_dir) and dir_util.is_empty(script.working_dir):
          file_util.remove(script.working_dir)
        return self._run_result(self.SCRIPT_CURRENT, None)
      build_blurb.blurb('build', '%s - building' % (script.descriptor.name))
      packager_result = script.execute({})
      if packager_result.success:
        return self._run_result(self.SCRIPT_SUCCESS, packager_result)
      else:
        return self._run_result(self.SCRIPT_FAILED, packager_result)

    except step_aborted as ex:
      return self._run_result(self.SCRIPT_ABORTED, None)

    assert False, 'Not Reached'
    return self._run_result(self.SCRIPT_FAILED, None)
  
  def build_many_scripts(self, package_names):

#    for name, script in self._env.script_manager.scripts.items():
#      self._env.checksum_manager.set_sources(script.descriptor.full_name, script.sources)
#    self._env.checksum_manager.print_sources()
    
    if self._env.config.no_checksums:
      self.blurb('removing checksums for: %s' % (' '.join(package_names)), fit = True)
      self.remove_checksums(package_names)
      for name in package_names:
        script = self._env.script_manager.scripts[name]
        self._env.checksum_manager.ignore(script.descriptor.full_name)

    if self._env.config.scratch:
      self.scratch_existing_data()

    if self._env.config.wipe:
      self.wipe_build_dirs(package_names)

    # Wipe build dirs older than 24 hours to prevent the tmp dir usage to grow unbounded
    self.wipe_old_build_dirs(self.package_names())
      
    if self._env.config.users:
      #
      # This whole section is broken
      #
      depends_on_packages = []
      for package_name in package_names:
        depends_on_packages += self._depends_on(package_name)
      depends_on_packages = algorithm.unique(depends_on_packages)
      package_names += depends_on_packages
    package_names = algorithm.unique(package_names)

    # If no package names are given we want them all
    package_names = package_names or self.package_names()

    tools_to_build = self._env.requirement_manager.resolve_tools(package_names, self._env.config.host_build_target.system)
    to_build = self._env.requirement_manager.resolve(package_names, self._env.config.host_build_target.system)

    tools_to_build_names = [ pd.name for pd in tools_to_build ]
    to_build_names = [ pd.name for pd in to_build ]
    
    save_build_target = self._env.config.build_target
    self._env.config.build_target = self._env.config.host_build_target
    exit_code = self._build_packages(tools_to_build_names, 'tools')
    self._env.config.build_target = save_build_target
    if exit_code != self.EXIT_CODE_SUCCESS:
      return exit_code

    return self._build_packages(to_build_names, 'packages')

  def _build_packages(self, packages_to_build, label):
    self.blurb('building %s: %s' % (label, ' '.join(packages_to_build)), fit = True)
    exit_code = self.EXIT_CODE_SUCCESS
    failed_packages = []
    for name in  packages_to_build:
      script = self._env.script_manager.scripts[name]
      filename = file_util.remove_head(script.filename, os.getcwd())
      if not script.enabled and not self._env.config.disabled:
        self.blurb('disabled: %s' % (filename))
        continue
      exit_code = self._call_build_script(script)
      if exit_code == self.EXIT_CODE_FAILED:
        failed_packages.append(name)
        if not self._env.config.keep_going:
          return self.EXIT_CODE_FAILED
      elif exit_code == self.EXIT_CODE_ABORTED:
        return self.EXIT_CODE_ABORTED

    if self._env.config.keep_going and failed_packages:
      self.blurb('failed packages: %s' % (' '.join(failed_packages)), fit = True)
      return self.EXIT_CODE_FAILED
      
    return exit_code

  def package_names(self):
    return self._env.script_manager.package_names()
  
  def _depends_on(self, what):
    'Return a list of package names for packages that depend on what.'
    result = []
    for _, script in self._env.script_manager.scripts.items():
      requirements_names = sorted([ req.name for req in script.descriptor.requirements + script.descriptor.build_requirements ])
      if what in requirements_names:
        result.append(script.descriptor.name)
    return result
