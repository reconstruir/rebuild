#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, fnmatch, os, os.path as path
from bes.common import algorithm, dict_util, object_util
from bes.thread import thread_pool
from bes.fs import dir_util, file_util
from bes.git import git_download_cache, git_util, repo as git_repo
from collections import namedtuple

from rebuild.source_finder import repo_source_finder

from rebuild import build_blurb, package_descriptor
from .rebuild_manager import rebuild_manager

from .build_script_runner import build_script_runner

class rebuild_builder(object):

  REBUILD_FILENAME = 'build.py'
  
  def __init__(self, config, build_target, tmp_dir, build_script_filenames):
    build_blurb.add_blurb(self, label = 'build')
    self._config = config
    self.build_target = build_target
    self._tmp_dir = path.abspath(tmp_dir)
    self._builds_tmp_dir = path.join(self._tmp_dir, 'builds', build_target.build_name)
    self._publish_dir = path.join(self._tmp_dir, 'artifacts')
    self._rebbe_root = path.join(self._tmp_dir, 'rebbe')
    self._downloads_root = path.join(self._tmp_dir, 'downloads')
    self._runner = build_script_runner(build_script_filenames, self.build_target)
    self.all_package_names = sorted(self._runner.scripts.keys())
    self.thread_pool = thread_pool(1)

  def exclude(self, excluded_packages):
    excluded_packages = object_util.listify(excluded_packages)
    for excluded_package in excluded_packages:
      if excluded_package in self._runner.scripts:
        del self._runner.scripts[excluded_package]

  def __match_arg_exact(self, arg):
    if arg in self._runner.scripts:
      return arg
    for package_name, script in self._runner.scripts.items():
      if script.filename.endswith(arg):
        return package_name
      p = path.normpath(path.join(arg, self.REBUILD_FILENAME))
      if script.filename.endswith(p):
        return package_name
    return None

  def __match_arg_with_pattern(self, arg):
    result = []
    pattern = '*%s*' % (arg)
    for package_name, script in self._runner.scripts.items():
      filename = path.relpath(script.filename)
      if fnmatch.fnmatch(filename, pattern):
        result.append(package_name)
    return result

  def __resolve_arg(self, arg):
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
      resolved_package_names = self.__resolve_arg(arg)
      if resolved_package_names:
        package_names.extend(resolved_package_names)
      else:
        invalid_args.append(arg)
    return self._resolved_args(package_names, invalid_args)

  def remove_checksums(self, package_names):
    'Remove checksums for the given packages given as package names.'
    rebbe = rebuild_manager(self._rebbe_root, None)
    scripts_todo = dict_util.filter_with_keys(self._runner.scripts, package_names)
    checksums_to_delete = [ script.package_info for script in scripts_todo.values() ]
    self.blurb('removing checksums: %s' % (' '.join(package_names)))
    rebbe.remove_checksums(checksums_to_delete, self.build_target)

  def wipe_build_dirs(self, package_names):
    patterns = [ '*%s-*' % (name) for name in package_names ]
    if path.isdir(self._builds_tmp_dir):
      self.blurb('cleaning temporary build directories in %s' % (path.relpath(self._builds_tmp_dir)))
      tmp_dirs = dir_util.list(self._builds_tmp_dir, patterns = patterns)
      file_util.remove(tmp_dirs)

  EXIT_CODE_SUCCESS = 0
  EXIT_CODE_FAILED = 1
  EXIT_CODE_ABORTED = 2

  def _run_build_script(self, script, opts):
    result = self._runner.run_build_script(script,
                                           self._config,
                                           tmp_dir = self._builds_tmp_dir,
                                           publish_dir = self._publish_dir,
                                           rebbe_root = self._rebbe_root,
                                           downloads_root = self._downloads_root,
                                           **opts)
    if result.status == build_script_runner.SUCCESS:
      self.blurb('%s - SUCCESS' % (script.package_info.name))
      return self.EXIT_CODE_SUCCESS
    elif result.status == build_script_runner.FAILED:
      print(result.packager_result.message)
      self.blurb('step failed - %s' % (result.packager_result.failed_step.__class__.__name__))
      self.blurb('%s - FAILED' % (script.package_info.name))
      return self.EXIT_CODE_FAILED
    elif result.status == build_script_runner.CURRENT:
      self.blurb('%s - up-to-date.' % (script.package_info.name))
      return self.EXIT_CODE_SUCCESS
    elif result.status == build_script_runner.ABORTED:
      self.blurb('aborted')
      return self.EXIT_CODE_ABORTED
    assert False
    return self.EXIT_CODE_FAILED

  def build_many_scripts(self, package_names, opts):

#    for name, script in self._runner.scripts.items():
#      self._config.checksum_manager.set_sources(script.package_info.full_name, script.sources)
#    self._config.checksum_manager.print_sources()
    
    if self._config.no_checksums:
      self.blurb('removing checksums for: %s' % (' '.join(package_names)), fit = True)
      self.remove_checksums(package_names)
      for name in package_names:
        script = self._runner.scripts[name]
        self._config.checksum_manager.ignore(script.package_info.full_name)
      
    if self._config.wipe:
      self.blurb('wiping build dirs for: %s' % (' '.join(package_names)), fit = True)
      self.wipe_build_dirs(package_names)

    opts = copy.deepcopy(opts)
    self.blurb_verbose('opts:\n%s' % (dict_util.dumps(opts)))
    if self._config.users:
      depends_on_packages = []
      for package_name in package_names:
        depends_on_packages += self.__depends_on(package_name)
      depends_on_packages = algorithm.unique(depends_on_packages)
      package_names += depends_on_packages
    package_names = algorithm.unique(package_names)

#      if self._config.tools_only and not script.package_info.is_tool():
#        self.blurb('skipping non tool: %s' % (filename))
#        continue
    
    resolved_package_names = self.__resolve_package_names(package_names)

    resolved_scripts = dict_util.filter_with_keys(self._runner.scripts, resolved_package_names)
    build_order_flat = build_script_runner.build_order_flat(resolved_scripts, self.build_target.system)

    if self._config.deps_only:
      for package_name in package_names:
        build_order_flat.remove(package_name)
    
    self.blurb('building packages: %s' % (' '.join(build_order_flat)), fit = True)
    
    exit_code = self.EXIT_CODE_SUCCESS

    failed_packages = []
    for name in  build_order_flat:
      script = self._runner.scripts[name]
      filename = file_util.remove_head(script.filename, os.getcwd())
      if script.disabled and not self._config.disabled:
        self.blurb('disabled: %s' % (filename))
        continue
      exit_code = self._run_build_script(script, opts)
      if exit_code == self.EXIT_CODE_FAILED:
        failed_packages.append(name)
        if not self._config.keep_going:
          return self.EXIT_CODE_FAILED
      elif exit_code == self.EXIT_CODE_ABORTED:
        return self.EXIT_CODE_ABORTED

    if self._config.keep_going and failed_packages:
      self.blurb('failed packages: %s' % (' '.join(failed_packages)), fit = True)
      return self.EXIT_CODE_FAILED
      
    return exit_code

  def __resolve_package_names(self, package_names):
    if not package_names:
      package_names = self.all_package_names
    return build_script_runner.resolve_requirements(self._runner.scripts, package_names, self.build_target.system)

  def __depends_on(self, what):
    'Return a list of package names for packages that depend on what.'
    result = []
    for _, script in self._runner.scripts.items():
      requirements_names = sorted([ req.name for req in script.package_info.requirements ])
      if what in requirements_names:
        result.append(script.package_info.name)
    return result

  def package_info(self, package_name):
    'Return the package info for a package.'
    return self._runner.scripts[package_name].package_info

#  @property
#  def publish_dir(self):
#    assert False
#    return self._publish_dir
