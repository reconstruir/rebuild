#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
#sys.dont_write_bytecode = True
import argparse, copy, os, os.path as path

from rebuild.base import build_arch, build_blurb, build_system, build_target, build_level
from bes.key_value import key_value_parser
from bes.fs import file_util

from bes.system import host
from bes.python import code

from .builder import builder
from .builder_config import builder_config
from .builder_env import builder_env

from bes.git import git_download_cache

class builder_cli(object):

  DEFAULT_OPTIONS = {
    'build_python': False,
  }

  def __init__(self):
    all_archs = ','.join(build_arch.DEFAULT_HOST_ARCHS)
    default_archs = ','.join(build_arch.DEFAULT_ARCHS[build_system.HOST])
    build_levels = ','.join(build_level.LEVELS)
    systems = ','.join(build_system.SYSTEMS)
    self.parser = argparse.ArgumentParser(description = 'Build packages.')
    self.parser.add_argument('-C', '--change-dir', action = 'store', type = str, default = None)
    self.parser.add_argument('-o', '--opts', action = 'store', type = str, default = '')
    self.parser.add_argument('-f', '--project-file', action = 'store', type = str, default = 'rebuild.project')
    self.parser.add_argument('-n', '--no-checksums', action = 'store_true')
    self.parser.add_argument('-v', '--verbose', action = 'store_true', default = False)
    self.parser.add_argument('-w', '--wipe', action = 'store_true')
    self.parser.add_argument('-k', '--keep-going', action = 'store_true')
    self.parser.add_argument('-d', '--disabled', action = 'store_true')
    self.parser.add_argument('-t', '--tools-only', action = 'store_true')
    self.parser.add_argument('-u', '--users', action = 'store_true', help = 'Rebuild users of given packages [ None ]')
    self.parser.add_argument('-j', '--jobs', action = 'store', type = int, help = 'Number of threads to use [ 1 ]')
    self.parser.add_argument('-s', '--system', action = 'store', type = str, default = build_target.DEFAULT, help = 'build_system.  One of (%s) [ %s ]' % (systems, build_system.DEFAULT))
    self.parser.add_argument('-a', '--archs', action = 'store', type = str, default = build_target.DEFAULT, help = 'Architectures to build for.  One of (%s) [ %s ]' % (all_archs, default_archs))
    self.parser.add_argument('-l', '--level', action = 'store', type = str, default = build_target.DEFAULT, help = 'Build level.  One of (%s) [ %s ]' % (build_levels, build_level.DEFAULT_LEVEL))
    self.parser.add_argument('--skip-to-step', action = 'store', type = str, help = 'Skip to the given step name. [ None ]')
    self.parser.add_argument('--deps-only', action = 'store_true', help = 'Only build dependencies')
    self.parser.add_argument('--no-network', action = 'store_true', help = 'Down go to the network.')
    self.parser.add_argument('--skip-tests', action = 'store_true', help = 'Skip the tests part of the build.')
    self.parser.add_argument('--scratch', action = 'store_true', help = 'Start from scratch by deleting existing data.')
    self.parser.add_argument('--filter', nargs = '+', default = None, help = 'filter the list of build files to the given list.')
    self.parser.add_argument('-r', '--root', action = 'store', type = str, default = 'BUILD', help = 'Root dir where to store the build.')
    self.parser.add_argument('target_packages', action = 'append', nargs = '*', type = str)
    self.parser.add_argument('--tps-address', default = builder_config.DEFAULT_THIRD_PARTY_ADDRESS,
                             action = 'store', type = str,
                             help = 'Third party sources address. [ %s ]' % (builder_config.DEFAULT_THIRD_PARTY_ADDRESS))
    self.parser.add_argument('--source-dir', default = None, action = 'store', type = str,
                             help = 'Local source directory to use instead of tps address. [ None]')
    self.parser.add_argument('--third-party-prefix', default = builder_config.DEFAULT_THIRD_PARTY_PREFIX,
                             action = 'store', type = str,
                             help = 'Prefix for third party source binaries. [ %s _]' % (builder_config.DEFAULT_THIRD_PARTY_PREFIX))
    self.parser.add_argument('--timestamp', default = None, action = 'store', type = str,
                             help = 'Timestamp to use for build working build directory droppings.  For predictable unit tests. [ None]')
    self.parser.add_argument('--performance', default = None, action = 'store_true',
                             help = 'Print performance information. [ None]')
    for g in self.parser._action_groups:
      g._group_actions.sort(key = lambda x: x.dest)
    
  def main(self):
    args = self.parser.parse_args()
    args.verbose = bool(args.verbose)

    if args.change_dir:
      os.chdir(args.change_dir)

    target_packages = args.target_packages[0]
    opts = copy.deepcopy(self.DEFAULT_OPTIONS)
    parsed_opts = key_value_parser.parse_to_dict(args.opts)
    opts.update(parsed_opts)

    available_packages = self.load_project_file(args.project_file)

    if args.filter:
      if path.isfile(args.filter[0]):
        target_packages_filter = file_util.read(args.filter[0]).split('\n')
      else:
        target_packages_filter = args.filter[0].split(',')
      target_packages_filter = [ p for p in target_packages_filter if p ]
      available_packages = self._filter_target_packages(available_packages, target_packages_filter)
    
    if 'system' in opts and args.system == build_target.DEFAULT:
      args.system == opts['system']

    if 'build_level' in opts and args.level == build_target.DEFAULT:
      args.level == opts['build_level']

    if 'archs' in opts and args.archs == build_target.DEFAULT:
      args.archs == opts['archs']
  
    args.system = build_system.parse_system(args.system)
    args.level = build_level.parse_level(args.level)
    args.archs = build_arch.parse_archs(args.system, args.archs)
    
    opts['system'] = args.system
    opts['level'] = args.level
    opts['archs'] = args.archs

    build_blurb.set_process_name('rebuild')
    build_blurb.set_verbose(args.verbose)

    config = builder_config()
    config.build_root = path.abspath(path.abspath(args.root))
    config.build_target = build_target(opts.get('system', build_target.DEFAULT),
                                       opts.get('build_level', build_target.DEFAULT),
                                       opts.get('archs', build_target.DEFAULT))
    config.deps_only = args.deps_only
    config.disabled = args.disabled
    config.keep_going = args.keep_going
    config.no_checksums = args.no_checksums
    config.no_network = args.no_network
    config.skip_tests = args.skip_tests
    config.skip_to_step = args.skip_to_step
    config.source_dir = args.source_dir
    config.tools_only = args.tools_only
    config.third_party_address = args.tps_address
    config.users = args.users
    config.verbose = args.verbose
    config.wipe = args.wipe
    config.scratch = args.scratch
    config.third_party_prefix = args.third_party_prefix
    if args.timestamp:
      config.timestamp = args.timestamp
    config.performance = args.performance
    env = builder_env(config, available_packages)
    
    build_blurb.blurb('rebuild', 'target=%s; host=%s' % (config.build_target.build_path, config.host_build_target.build_path))

    bldr = builder(env)

    resolved_args = bldr.check_and_resolve_cmd_line_args(target_packages)
      
    if resolved_args.invalid_args:
      build_blurb.blurb('rebuild', 'Invalid targets: %s' % (' '.join(resolved_args.invalid_args)))
      build_blurb.blurb('rebuild', 'possible targets:')
      build_blurb.blurb('rebuild', ' '.join(bldr.package_names()), fit = True)
      return 1

    return bldr.build_many_scripts(resolved_args.package_names)

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
    raise SystemExit(builder_cli().main())

  @classmethod
  def load_project_file(clazz, filename):
    if not path.exists(filename):
      raise RuntimeError('rebuild project file not found: %s' % (filename))
    tmp_globals = {}
    tmp_locals = {}
    code.execfile(filename, tmp_globals, tmp_locals)
    if not 'rebuild_packages' in tmp_locals:
      raise RuntimeError('rebuild_packages not defined: %s' % (filename))
    func = tmp_locals['rebuild_packages']
    if not callable(func):
      raise RuntimeError('not callable: %s' % (func))
    return func()
