#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import glob, os, os.path as path
from bes.common.algorithm import algorithm
from bes.common.string_list_util import string_list_util
from bes.system import execute
from bes.fs import dir_util, file_util
from rebuild.native_package_manager import native_package_manager as npm
from bes.match import matcher_util
from rebuild.toolchain import library

from .config_file import config_file
from .sync import sync

class jail(object):

  @classmethod
  def create(clazz, dst_dir, config, no_filters):
    'Create a jail at dst_dir with config.'
    if not isinstance(config, config_file):
      raise RuntimeError('Not a config_file: %s' % (str(config)))
    if path.exists(dst_dir):
      if not path.isdir(dst_dir):
        raise RuntimeError('Not a directory: %s' % (dst_dir))
      if not dir_util.is_empty(dst_dir):
        raise RuntimeError('Directory should be empty: %s' % (dst_dir))
    else:
      file_util.mkdir(dst_dir)

    clazz.__install_packages(dst_dir, config, no_filters)
    clazz.__install_binaries(dst_dir, config, no_filters)

    for post_hook in config.jail.hooks.post or []:
      #print "executing: ", post_hook
      execute.execute(post_hook)

  @classmethod
  def __install_packages(clazz, dst_dir, config, no_filters):
    'Install jail packages.'
    for package in config.jail.packages:
      if not npm.is_installed(package.name):
        raise RuntimeError('Package not installed: %s' % (package.name))
      files = npm.package_contents(package.name)
      if no_filters:
        include = None
        exclude = None
      else:
        include = package.include or []
        exclude = package.exclude or []
      filtered_files = matcher_util.match_filenames(files, include, exclude)
      src_dir = '/'
      sync.sync_files(src_dir, dst_dir, filtered_files, package.name)
  
  @classmethod
  def __install_binaries(clazz, dst_dir, config, no_filters):
    'Install jail binaries.'
    # FIXME: split this into a list so the blurb is the binary name instead of 'binaries'
    resolved_binaries = clazz.__resolve_binaries(config.jail.binaries or [])
    files = clazz.__manifest_for_binaries(resolved_binaries)
    src_dir = '/'
    sync.sync_files(src_dir, dst_dir, files, 'binaries')
  
  @classmethod
  def __resolve_binaries(clazz, binaries):
    'Resolve binaries.'
    files = []
    for binary in binaries:
      files.extend(glob.glob(binary))
    return files
  
  @classmethod
  def __manifest_for_binaries(clazz, binaries):
    'Install jail binaries.'
    files = set()
    for binary in binaries:
      if not path.isfile(binary):
        raise RuntimeError('not found: %s' % (binary))
      deps = library.dependencies_recursive(binary)
      files.add(binary)
      for p in dir_util.all_parents(binary):
        files.add(p)
      for dep in deps:
        files.add(dep)
        for p in dir_util.all_parents(dep):
          files.add(p)
    string_list_util.remove_if(files, '/')
    return sorted(algorithm.unique(list(files)))
