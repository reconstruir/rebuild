#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
#sys.dont_write_bytecode = True
import argparse, os, os.path as path

from bes.build.build_arch import build_arch
from bes.build.build_blurb import build_blurb
from bes.build.build_level import build_level
from bes.build.build_system import build_system
from bes.build.build_target import build_target
from bes.build.build_target_cli import build_target_cli
from rebuild.project.project_file_parser import project_file_parser
from rebuild.project.project_file import project_file

from rebuild.project.project_file_manager import project_file_manager

# needed so that artifact_manager_artifactory ends up in the standalone package
from rebuild.package.artifact_manager_artifactory import artifact_manager_artifactory

from bes.fs.file_util import file_util

from .builder import builder
from .builder_config import builder_config
from .builder_env import builder_env

class builder_cli(build_target_cli):

  def __init__(self):
    self.parser = argparse.ArgumentParser(description = 'Build packages.')
    self.build_target_add_arguments(self.parser)
    self.parser.add_argument('-C', '--change-dir', action = 'store', type = str, default = None)
    self.parser.add_argument('-f', '--project-file', action = 'store', type = str, default = 'rebuild.reproject')
    self.parser.add_argument('-o', '--override-projects', action = 'store', type = str, default = None, help = 'Override projects with the content of the given project file [ None ]')
    self.parser.add_argument('-n', '--no-checksums', action = 'store_true')
    self.parser.add_argument('-p', '--python-version', action = 'store',
                             default = builder_config.DEFAULT_PYTHON_VERSION)
    self.parser.add_argument('--print-step-values', action = 'store_true')
    self.parser.add_argument('--print-sources', action = 'store_true')
    self.parser.add_argument('--print-variables', action = 'store_true')
    self.parser.add_argument('--print-properties', action = 'store_true')
    self.parser.add_argument('-v', '--verbose', action = 'store_true', default = False)
    self.parser.add_argument('-w', '--wipe', action = 'store_true')
    self.parser.add_argument('-k', '--keep-going', action = 'store_true')
    self.parser.add_argument('--disabled', action = 'store_true')
    self.parser.add_argument('-t', '--tools-only', action = 'store_true')
    self.parser.add_argument('-u', '--users', action = 'store_true', help = 'Rebuild users of given packages [ None ]')
    self.parser.add_argument('-j', '--jobs', action = 'store', type = int, help = 'Number of threads to use [ 1 ]')
    self.parser.add_argument('--skip-to-step', action = 'store', type = str, help = 'Skip to the given step name. [ None ]')
    self.parser.add_argument('--deps-only', action = 'store_true', help = 'Only build dependencies')
    self.parser.add_argument('--recipes-only', action = 'store_true', help = 'Only read the recipes dont build them.')
    self.parser.add_argument('--no-network', action = 'store_true', help = 'Down go to the network.')
    self.parser.add_argument('--no-tests', action = 'store_true', help = 'Skip the tests part of the build.')
    self.parser.add_argument('--targets', action = 'store_true', help = 'Print the possible targets.')
    self.parser.add_argument('--scratch', action = 'store_true', help = 'Start from scratch by deleting existing data.')
    self.parser.add_argument('--filter', nargs = '+', default = None, help = 'filter the list of build files to the given list.')
    self.parser.add_argument('-r', '--root', action = 'store', type = str, default = 'BUILD', help = 'Root dir where to store the build.')
    self.parser.add_argument('target_packages', action = 'append', nargs = '*', type = str)
    self.parser.add_argument('--third-party-prefix', default = builder_config.DEFAULT_THIRD_PARTY_PREFIX,
                             action = 'store', type = str,
                             help = 'Prefix for third party source binaries. [ %s _]' % (builder_config.DEFAULT_THIRD_PARTY_PREFIX))
    self.parser.add_argument('--timestamp', default = None, action = 'store', type = str,
                             help = 'Timestamp to use for build working build directory droppings.  For predictable unit tests. [ None]')
    self.parser.add_argument('--performance', default = None, action = 'store_true',
                             help = 'Print performance information. [ None ]')
    self.parser.add_argument('--download-only', default = None, action = 'store_true',
                             help = 'Only download stuff needed for the build without building anything. [ True ]')
    self.parser.add_argument('--storage-config', default = None, #'config/new_storage.config',
                             action = 'store', type = str,
                             help = 'Configuration file for storage used for artifacts and sources upload/download. [ None ]')
    self.parser.add_argument('--sources-config-name', default = 'local',
                             action = 'store', type = str,
                             help = 'The storage provider to use for sources. [ local ]')
    self.parser.add_argument('--artifacts-config-name', default = None,
                             action = 'store', type = str,
                             help = 'The storage provider to use for artifacts. [ None ]')
    self.parser.add_argument('--ingest', action = 'store_true', help = 'Execute all the ingest build steps. [ False ]')
    self.parser.add_argument('--ingest-only', default = None, action = 'store_true',
                             help = 'Only ingest stuff needed for the build without building anything. [ True ]')
    self.parser.add_argument('--version', default = None, action = 'store_true',
                             help = 'Only print the version. [ True ]')
    self.parser.add_argument('--var', default = [], action = 'append', metavar = ( 'key', 'value' ), nargs = 2,
                             help = 'Add or override environment variables. [ None ]')
    self.parser.add_argument('--checksum-cache', default = None,
                             action = 'store', type = str,
                             help = 'The checksum cache to speed up builds. [ None ]')
    self.parser.add_argument('--profile', action = 'store_true', help = 'Use cProfile to profile. [ False ]')
    self.parser.add_argument('--ignore-install-file-errors', action = 'store_true', help = 'Ignore install_files errors. [ False ]')
    self.parser.add_argument('--properties-file', default = None, action = 'store', type = str,
                             help = 'Properties file to add or override environment variables. [ None ]')

    for g in self.parser._action_groups:
      g._group_actions.sort(key = lambda x: x.dest)

  def main(self):
    args = self.parser.parse_args()
    if args.profile:
      import cProfile
      cp = cProfile.Profile()
      cp.enable()
    exit_code = self._real_main(args)
    if args.profile:
      cp.dump_stats('rebuilder.cprofile')
    raise SystemExit(exit_code)

  def _real_main(self, args):
    bt = self.build_target_resolve(args)
    args.verbose = bool(args.verbose)

    build_blurb.set_process_name('rebuild')
    build_blurb.set_verbose(args.verbose)

    if args.version:
      from bes.version.version_cli import version_cli
      version_cli.print_everything('rebuild', dependencies = [ 'bes' ], print_all = args.verbose)
      return 0

    build_blurb.blurb_verbose('rebuild', 'command line: %s' % (' '.join(sys.argv)))
    
    if args.change_dir:
      os.chdir(args.change_dir)

    target_packages = args.target_packages[0]

    checksum_getter = self._make_checksum_getter(args.checksum_cache)

    pfm = project_file_manager(checksum_getter)
    pfm.load_project_files_from_env()
    pfm.load_project_file(args.project_file)
    if args.override_projects:
      if not pfm.override_projects(args.override_projects):
        build_blurb.blurb('rebuild', 'failed to override projects:  %s' % (args.override_projects))
        return 1

    if args.print_variables:
      pfm.print_variables()
      return 0
      
    available_packages = pfm.available_recipes(args.project_file, bt)
    imported_projects = pfm.imported_projects(args.project_file, bt)
    for p in imported_projects:
      relp = path.relpath(p)
      blurbp = relp if not relp.startswith(path.pardir) else p
      build_blurb.blurb('rebuild', 'imported project %s' % (blurbp))
    
    if args.filter:
      if path.isfile(args.filter[0]):
        target_packages_filter = file_util.read(args.filter[0]).split('\n')
      else:
        target_packages_filter = args.filter[0].split(',')
      target_packages_filter = [ p for p in target_packages_filter if p ]
      available_packages = self._filter_target_packages(available_packages, target_packages_filter)

    # Tests only run on desktop
    if not bt.is_desktop():
      args.no_tests = True

    if args.no_network:
      if args.download_only:
        build_blurb.blurb('rebuild', 'Only one of --download-only and --no-net can be given.')
        return 1
      if args.ingest_only:
        build_blurb.blurb('rebuild', 'Only one of --ingest-only and --no-net can be given.')
        return 1

    if args.download_only and args.ingest_only:
      build_blurb.blurb('rebuild', 'Only one of --download-only and --ingest-only can be given.')
      return 1
      
    config = builder_config()
    config.build_root = path.abspath(path.abspath(args.root))
    config.build_target = bt
    config.deps_only = args.deps_only
    config.recipes_only = args.recipes_only
    config.disabled = args.disabled
    config.keep_going = args.keep_going
    config.no_checksums = args.no_checksums
    config.no_network = args.no_network
    config.no_tests = args.no_tests
    config.skip_to_step = args.skip_to_step
    config.tools_only = args.tools_only
    config.users = args.users
    config.verbose = args.verbose
    config.wipe = args.wipe
    config.scratch = args.scratch
    config.third_party_prefix = args.third_party_prefix
    if args.timestamp:
      config.timestamp = args.timestamp
    config.performance = args.performance
    config.download_only = args.download_only
    config.storage_config = args.storage_config
    config.sources_config_name = args.sources_config_name
    config.artifacts_config_name = args.artifacts_config_name
    config.ingest = args.ingest or args.ingest_only
    config.ingest_only = args.ingest_only
    if config.ingest_only:
      config.no_tests = True

    config.project_file = path.abspath(args.project_file)
      
    config.project_file_variables = pfm.available_variables(args.project_file,
                                                            config.build_target)

    config.cli_variables = args.var
    config.ignore_install_file_errors = args.ignore_install_file_errors
    config.properties_file = args.properties_file
    config.python_version = args.python_version

    env = builder_env(config, available_packages, checksum_getter, pfm)
    
    if args.print_step_values:
      env.script_manager.print_step_values()
      return 0
    
    if args.print_sources:
      env.script_manager.print_sources()
      return 0

    if args.print_properties:
      env.print_properties()
      return 0
    
    bldr = builder(env)

    resolved_args = bldr.check_and_resolve_cmd_line_args(target_packages)

    if args.targets:
      build_blurb.blurb('rebuild', ' '.join(bldr.package_names()), fit = True)
      return 1

    build_blurb.blurb('rebuild', 'target=%s; host=%s' % (config.build_target.build_path, config.host_build_target.build_path))

    if resolved_args.invalid_args:
      build_blurb.blurb('rebuild', 'Invalid targets: %s' % (' '.join(resolved_args.invalid_args)))
      build_blurb.blurb('rebuild', 'possible targets:')
      build_blurb.blurb('rebuild', ' '.join(bldr.package_names()), fit = True)
      return 1

    if config.recipes_only:
      return bldr.EXIT_CODE_SUCCESS
    
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
    #import cProfile
    #cp = cProfile.Profile()
    #cp.enable()
    exit_code = builder_cli().main()
    #cp.dump_stats('rebuilder.cprofile')
    raise SystemExit(exit_code)

  @classmethod
  def _make_checksum_getter(clazz, checksum_cache):
    from bes.fs.file_checksum_getter_db import file_checksum_getter_db
    from bes.fs.file_checksum_getter_raw import file_checksum_getter_raw
    if checksum_cache:
      cache_filename = path.expanduser(checksum_cache)
      return file_checksum_getter_db(cache_filename)
    else:
      return file_checksum_getter_raw()
