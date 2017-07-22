#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import sys
#sys.dont_write_bytecode = True
import argparse, copy, os, os.path as path

from rebuild import build_arch, build_type, build_blurb, build_target, System
from rebuild.packager import rebuild_builder
from bes.key_value import key_value_parser
from bes.fs import file_util

from bes.archive import archiver
from bes.common import string_util
from bes.system import host

from rebuild.packager import rebuild_manager
from rebuild.package_manager import artifact_manager, Package, package_tester
from rebuild.tools_manager import tools_manager

class rebuilder_cli(object):

  DEFAULT_OPTIONS = {
    'build_python': False,
  }

  def __init__(self):
    all_archs = ','.join(build_arch.ARCHS[System.HOST])
    default_archs = ','.join(build_arch.DEFAULT_ARCHS[System.HOST])
    build_types = ','.join(build_type.BUILD_TYPES)
    systems = ','.join(System.SYSTEMS)
    self.parser = argparse.ArgumentParser(description = 'Build packages.')
    self.parser.add_argument('-o', '--opts', action = 'store', type = str, default = '')
    self.parser.add_argument('-f', '--rebuildstruct', action = 'store', type = str, default = 'rebuildstruct')
    self.parser.add_argument('-n', '--no-checksums', action = 'store_true')
    self.parser.add_argument('-v', '--verbose', action = 'store_true')
    self.parser.add_argument('-w', '--wipe', action = 'store_true')
    self.parser.add_argument('-k', '--keep-going', action = 'store_true')
    self.parser.add_argument('-d', '--disabled', action = 'store_true')
    self.parser.add_argument('-t', '--tools-only', action = 'store_true')
    self.parser.add_argument('-u', '--users', action = 'store_true', help = 'Rebuild users of given packages [ None ]')
    self.parser.add_argument('-j', '--jobs', action = 'store', type = int, help = 'Number of threads to use [ 1 ]')
    self.parser.add_argument('-s', '--system', action = 'store', type = str, default = build_target.DEFAULT, help = 'System.  One of (%s) [ %s ]' % (systems, System.DEFAULT))
    self.parser.add_argument('-a', '--archs', action = 'store', type = str, default = build_target.DEFAULT, help = 'Architectures to build for.  One of (%s) [ %s ]' % (all_archs, default_archs))
    self.parser.add_argument('-b', '--build-type', action = 'store', type = str, default = build_target.DEFAULT, help = 'Build type.  One of (%s) [ %s ]' % (build_types, build_type.DEFAULT_BUILD_TYPE))
    self.parser.add_argument('-skip-to-step', action = 'store', type = str, help = 'Skip to the given step name. [ None ]')
    self.parser.add_argument('--deps-only', action = 'store_true', help = 'Only build dependencies')
    self.parser.add_argument('--filter', nargs = '+', default = None, help = 'filter the list of build files to the given list.')
    self.parser.add_argument('--tmp-dir', action = 'store', type = str, default = path.abspath('tmp'), help = 'Temporary directory for storing builds and artifacts')
    self.parser.add_argument('target_packages', action = 'append', nargs = '*', type = str)
    
  def main(self):
    args = self.parser.parse_args()

    target_packages = args.target_packages[0]
    opts = copy.deepcopy(self.DEFAULT_OPTIONS)
    parsed_opts = key_value_parser.parse_to_dict(args.opts)
    opts.update(parsed_opts)

    available_packages = self.load_structure_file(args.rebuildstruct)
    
    if args.filter:
      if path.isfile(args.filter[0]):
        target_packages_filter = file_util.read(args.filter[0]).split('\n')
      else:
        target_packages_filter = args.filter[0].split(',')
      target_packages_filter = [ p for p in target_packages_filter if p ]
      available_packages = self._filter_target_packages(available_packages, target_packages_filter)
    
    if 'system' in opts and args.system == build_target.DEFAULT:
      args.system == opts['system']

    if 'build_type' in opts and args.build_type == build_target.DEFAULT:
      args.build_type == opts['build_type']

    if 'archs' in opts and args.archs == build_target.DEFAULT:
      args.archs == opts['archs']
  
    args.system = System.parse_system(args.system)
    args.build_type = build_type.parse_build_type(args.build_type)
    args.archs = build_arch.parse_archs(args.system, args.archs)

    opts['system'] = args.system
    opts['build_type'] = args.build_type
    opts['archs'] = args.archs

    build_blurb.set_process_name('build')
    build_blurb.set_verbose(bool(args.verbose))

    tmp_dir = args.tmp_dir

    filenames = [ path.join(p, 'build.py') for p in available_packages ]

    bt = build_target(opts.get('system', build_target.DEFAULT),
                      opts.get('build_type', build_target.DEFAULT),
                      opts.get('archs', build_target.DEFAULT))

    build_blurb.blurb('build', 'build_target: %s' % (str(bt)))

    builder = rebuild_builder(bt, tmp_dir, filenames)
    resolved_args = builder.check_and_resolve_cmd_line_args(target_packages)
      
    if resolved_args.invalid_args:
      build_blurb.blurb('build', 'Invalid targets: %s' % (' '.join(resolved_args.invalid_args)))
      build_blurb.blurb('build', 'possible targets:')
      build_blurb.blurb('build', ' '.join(builder.all_package_names), fit = True)
      return 1

    if args.no_checksums:
      builder.remove_checksums(resolved_args.package_names)

    if args.wipe:
      builder.wipe_build_dirs(resolved_args.package_names)

    config = rebuild_builder.builder_config(args.keep_going,
                                            args.disabled,
                                            args.users,
                                            args.deps_only,
                                            args.skip_to_step,
                                            args.tools_only)
    
    return builder.build_many_scripts(resolved_args.package_names, config, opts)

  @classmethod
  def _filter_target_packages(clazz, target_packages, limit):
    if not limit:
      return target_packages
    result = []
    for p in target_packages:
      for l in limit:
        if l in p:
          result.append(p)
    return result
  
  @classmethod
  def run(clazz):
    raise SystemExit(rebuilder_cli().main())

  @classmethod
  def load_structure_file(clazz, filename):
    if not path.exists(filename):
      raise RuntimeError('rebuild structure file not found: %s' % (filename))
    tmp_globals = {}
    tmp_locals = {}
    execfile(filename, tmp_globals, tmp_locals)
    if not 'rebuild_subdirs' in tmp_locals:
      raise RuntimeError('rebuild_subdirs not defined: %s' % (filename))
    func = tmp_locals['rebuild_subdirs']
    if not callable(func):
      raise RuntimeError('not callable: %s' % (func))
    return func()
      
