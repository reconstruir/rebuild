#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, fnmatch, os, os.path as path, threading
from bes.common import algorithm, check, dict_util, object_util
from bes.thread import thread_pool
from bes.fs import dir_util, file_util
from bes.dependency import dependency_resolver
from collections import namedtuple
from rebuild.step import step_aborted
from rebuild.base import build_blurb
from rebuild.package.db_error import *

from .builder_script import builder_script

class builder(object):

  REBUILD_FILENAME = 'build.py'
  
  def __init__(self, env):
    build_blurb.add_blurb(self, label = 'rebuild')
    self._env = env
    self.thread_pool = thread_pool(1)

  def exclude(self, excluded_packages):
    excluded_packages = object_util.listify(excluded_packages)
    for excluded_package in excluded_packages:
      if excluded_package in self._env.script_manager.scripts:
        del self._env.script_manager.scripts[excluded_package]

  def _match_arg_exact(self, arg):
    if arg in self._env.script_manager.scripts:
      return arg
    for package_name, script in self._env.script_manager.scripts.items():
      if script.filename.endswith(arg):
        return package_name
      p = path.normpath(path.join(arg, self.REBUILD_FILENAME))
      if script.filename.endswith(p):
        return package_name
    return None

  def _match_arg_with_pattern(self, arg):
    result = []
    pattern = '*%s*' % (arg)
    for package_name, script in self._env.script_manager.scripts.items():
      filename = path.relpath(script.filename)
      if fnmatch.fnmatch(filename, pattern):
        result.append(package_name)
    return result

  def _resolve_arg(self, arg):
    exact_match = self._match_arg_exact(arg)
    if exact_match:
      return [ exact_match ]
    result = self._match_arg_with_pattern(arg)
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
    self.blurb('scratching existing data: %s' % (' '.join([ path.relpath(d) for d in dirs ])))
    for d in dirs:
      file_util.remove(d)
    # Since we just killed the directory where the artifacts db lives we need to reload it
    self._env.reload_artifact_manager()
    
  def wipe_old_build_dirs(self, package_names):
    for package_name in package_names:
      script = self._env.script_manager.scripts[package_name]
      builds_dir = self._env.config.builds_dir(script.build_target)
      to_remove = []
      if path.isdir(builds_dir):
        tmp_dirs = dir_util.older_dirs(dir_util.list(builds_dir), hours = 24)
        for tmp_dir in tmp_dirs:
          self._env.trash.trash(tmp_dir)
#          self.blurb('wiping expired tmp build directory: %s' % (path.relpath(tmp_dir)))
#          to_remove.append(tmp_dir)

      def remove_tmp_dirs_thread(dirs):
        for d in dirs:
          file_util.remove(d)

      t = threading.Thread(target = remove_tmp_dirs_thread, args = (to_remove, ))
      t.start()

  EXIT_CODE_SUCCESS = 0
  EXIT_CODE_FAILED = 1
  EXIT_CODE_ABORTED = 2

  def _call_build_one_script(self, script):
    result = self._build_one_script(script, self._env)
    if result.status == self.SCRIPT_SUCCESS:
      if self._env.config.download_only:
        label = 'DOWNLOADED'
      elif self._env.config.ingest_only:
        label = 'INGESTED'
      else:
        label = 'SUCCESS'
      self.blurb('%s - %s' % (script.descriptor.name, label))
      return self.EXIT_CODE_SUCCESS
    elif result.status == self.SCRIPT_FAILED:
      self.blurb('FAILED: %s - %s\n%s' % (script.descriptor.name, result.script_result.failed_step.__class__.__name__, result.script_result.message))
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
  _run_result = namedtuple('_run_result', 'status,script_result')
  
  def _build_one_script(self, script, env):
    if env.config.download_only:
      return self. _build_one_script_partial('downloading', script, env)
    elif env.config.ingest_only:
      return self. _build_one_script_partial('ingesting', script, env)
    else:
      try:
        return self._build_one_script_build(script, env)
      except step_aborted as ex:
        return self._run_result(self.SCRIPT_ABORTED, None)

    assert False, 'Not Reached'

  def _build_one_script_partial(self, label, script, env):
      build_blurb.blurb('rebuild', '%s - %s' % (script.descriptor.name, label))
      script_result = script.execute()
      if script_result.success:
        return self._run_result(self.SCRIPT_SUCCESS, script_result)
      else:
        return self._run_result(self.SCRIPT_FAILED, script_result)
  
  def _build_one_script_build(self, script, env):
    needs_rebuilding, reason = self._needs_rebuilding(script, env)
    if not needs_rebuilding:
      # If the working directory is empty, it means no work happened and its useless
      if path.exists(script.working_dir) and dir_util.is_empty(script.working_dir):
        file_util.remove(script.working_dir)
      return self._run_result(self.SCRIPT_CURRENT, None)
    build_blurb.blurb('rebuild', '%s - building because %s' % (script.descriptor.name, reason))
    script_result = script.execute()
    if script_result.success:
      return self._run_result(self.SCRIPT_SUCCESS, script_result)
    else:
      return self._run_result(self.SCRIPT_FAILED, script_result)

  def _needs_rebuilding(self, script, env):
    if env.checksum_manager.is_ignored(script.descriptor.full_name):
      return True, 'checksum_ignored'
    if env.external_artifact_manager:
      if env.external_artifact_manager.has_package_by_descriptor(script.descriptor, script.build_target):
        return False, 'package found in AM'
    return script.needs_rebuilding(), 'checksums'
    
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

    req_manager = self._env.requirement_manager

    test_hardness = []
    if not self._env.config.no_tests:
      test_hardness += [ 'TEST' ]
    
    to_build = self._resolve_and_order(package_names,
                                       self._env.config.host_build_target.system,
                                       [ 'BUILD', 'RUN' ] + test_hardness,
                                       lambda dep: not req_manager.is_tool(dep))

    tools_to_build = self._resolve_and_order(package_names,
                                             self._env.config.host_build_target.system,
                                             [ 'BUILD', 'RUN', 'TOOL' ] + test_hardness,
                                             lambda dep: req_manager.is_tool(dep))

    save_build_target = self._env.config.build_target

    if self._env.config.host_build_target != self._env.config.build_target:
      tools_to_build_scripts = self._scripts_clone_for_host_build_target(self._env.script_manager.subset(tools_to_build.names()),
                                                                         self._env.config.host_build_target,
                                                                         self._env)
    else:
      tools_to_build_scripts = self._env.script_manager.subset(tools_to_build.names())
    self._env.config.build_target = self._env.config.host_build_target
    exit_code = self._build_packages(tools_to_build_scripts,
                                     tools_to_build.names(),
                                     'tools')
    self._env.config.build_target = save_build_target

    if exit_code != self.EXIT_CODE_SUCCESS:
      return exit_code

    return self._build_packages(self._env.script_manager.scripts,
                                to_build.names(),
                                'packages')

  def _resolve_and_order(self, names, system, hardness, name_filter):
    'Resolve packages without tools return the names in build order.'
    assert callable(name_filter)
    check.check_string_seq(names)
    req_manager = self._env.requirement_manager
    just_deps = req_manager.resolve_deps(names, system, hardness, False)
    everything_names = algorithm.unique(just_deps.names() + names)
    only_wanted_names = [ dep for dep in everything_names if name_filter(dep) ]
    only_wanted_deps = req_manager.resolve_deps(only_wanted_names, system, hardness, False)
    wanted_everything_names = algorithm.unique(only_wanted_deps.names() + only_wanted_names)
    all_dep_map = req_manager.dependency_map(hardness, system)
    resolved_map = dict_util.filter_with_keys(all_dep_map, wanted_everything_names)
    return req_manager.descriptors(dependency_resolver.build_order_flat(resolved_map))
  
  @classmethod
  def _scripts_clone_for_host_build_target(clazz, scripts, host_build_target, env):
    result = {}
    for name, script in scripts.items():
      host_script = builder_script(script.recipe, host_build_target, env)
      result[name] = host_script
    return result
  
  def _build_packages(self, scripts, packages_to_build, label):
    self.blurb('building %s: %s' % (label, ' '.join(packages_to_build)), fit = True)
    exit_code = self.EXIT_CODE_SUCCESS
    failed_packages = []
    for name in  packages_to_build:
      script = scripts[name]
      filename = file_util.remove_head(script.filename, os.getcwd())
      if not script.enabled and not self._env.config.disabled:
        self.blurb('disabled: %s' % (filename))
        continue
      exit_code = self._call_build_one_script(script)
#      sources = script.sources()
#      for s in sources:
#        print('CACA: %s: SOURCE: %s' % (script.descriptor.name, s))
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
