#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, copy, os, os.path as path
from collections import namedtuple

from bes.system import log
from bes.archive import archiver
from bes.key_value import key_value_parser
from bes.system import host
from bes.fs import file_util, temp_file
from rebuild.base import build_arch, build_blurb, build_system, build_target, build_target_cli, build_level

from rebuild.package import artifact_manager_local, artifact_manager_artifactory
from rebuild.package.artifact_manager_artifactory import artifact_manager_artifactory

from rebuild.config import storage_config
#from .storage_factory import storage_factory

from .manager import manager
from .manager_script import manager_script

class tool_cli(build_target_cli):

  def __init__(self):
    log.add_logging(self, 'retool')
    self.parser = argparse.ArgumentParser()

    commands_subparser = self.parser.add_subparsers(help = 'commands', dest = 'command')

    # version
    self.packages_parser = commands_subparser.add_parser('version', help = 'Packages')
    
    # packages
    self.packages_parser = commands_subparser.add_parser('packages', help = 'Packages')
    self.packages_subparsers = self.packages_parser.add_subparsers(help = 'packages_commands', dest = 'subcommand')

    self.packages_subparsers.add_parser('update', help = 'Update installed packages')
    self.packages_subparsers.add_parser('print', help = 'Print installed packages')

    # packages:update
    update_parser = self.packages_subparsers.add_parser('update', help = 'Update packages')
    self._packages_add_common_args(update_parser)
    update_parser.add_argument('--wipe',
                               '-w',
                               action = 'store_true',
                               default = False,
                               help = 'Wipe the installation dir before updating [ False ]')
    update_parser.add_argument('--downgrade',
                               action = 'store_true',
                               default = False,
                               help = 'Allow downgrade of packages [ False ]')
    update_parser.add_argument('--force',
                               action = 'store_true',
                               default = False,
                               help = 'Force update of packages even if the version is the same [ False ]')
    update_parser.add_argument('--dont-touch-update-script',
                               action = 'store_true',
                               default = False,
                               help = 'Dont touch the update.sh script when done updating packages. [ False ]')
    update_parser.add_argument('project_name',
                               action = 'store',
                               default = None,
                               nargs='?',
                               help = 'Project name [ None ]')

    # packages:print
    print_parser = self.packages_subparsers.add_parser('print', help = 'Print packages')
    self._packages_add_common_args(print_parser)
    print_parser.add_argument('project_name',
                              action = 'store',
                              default = None,
                              nargs='?',
                              help = 'Project name [ None ]')
    
    # config
    self.config_parser = commands_subparser.add_parser('config', help = 'Config')
    self.config_subparsers = self.config_parser.add_subparsers(help = 'config_commands', dest = 'subcommand')

    # config:packages
    packages_parser = self.config_subparsers.add_parser('packages', help = 'Print information about config packages.')
    #self._packages_add_common_args(packages_parser)
    packages_parser.add_argument('project_name',
                                 action = 'store',
                                 default = None,
                                 help = 'Name of project [ None ]')

    # config:projects
    projects_parser = self.config_subparsers.add_parser('projects', help = 'Print information about config projects.')
    #self._packages_add_common_args(projects_parser)

  def _packages_add_common_args(self, parser):
    'Add common arguments for all the "packages" command'
    self.build_target_add_arguments(parser)
    parser.add_argument('root_dir',
                        action = 'store',
                        default = None,
                        help = 'The root directory [ None ]')
    parser.add_argument('storage_config', default = None,
                        action = 'store',
                        type = str,
                        help = 'Configuration file for storage used for artifacts and sources upload/download. [ None ]')
    parser.add_argument('artifacts_provider', default = 'local',
                        action = 'store',
                        type = str,
                        help = 'The storage provider to use for artifacts. [ local ]')
    parser.add_argument('--verbose',
                        '-v',
                        action = 'store_true',
                        default = False,
                        help = 'Verbose debug spew [ False ]')
    
  def _packages_check_common_args(self, command, args):
    'Add common arguments for all the "packages" commands.'
    if not path.isfile(args.storage_config):
      raise IOError('%s: storage config not found: %s' % (command, args.storage_config))
    
    self._storage_config_filename = args.storage_config
    self._storage_config = storage_config.from_file(self._storage_config_filename)
    self._artifacts_provider = args.artifacts_provider

    download_credentials = self._storage_config.get('download', self._artifacts_provider)
    self._local_storage_cache_dir = path.join(path.expanduser('~/.ego/storage_cache'), self._artifacts_provider)

    if self._artifacts_provider == 'local':
      artifacts_dir = path.join(download_credentials.values['location'], download_credentials.root_dir)
      self.artifact_manager = artifact_manager_local(artifacts_dir)
    elif self._artifacts_provider == 'artifactory':
      self.artifact_manager = artifact_manager_artifactory(self._local_storage_cache_dir, self._storage_config)
    else:
      assert False
    
  def main(self):
    args = self.parser.parse_args()
    if getattr(args, 'system', None) is not None:
      self.build_target = self.build_target_resolve(args)
    subcommand = getattr(args, 'subcommand', None)
    if subcommand:
      command = '%s:%s' % (args.command, subcommand)
    else:
      command = args.command

    self.verbose = getattr(args, 'verbose', False)

    if self.verbose:
      log.configure('retool*=info format=brief width=20')
      
    if command.startswith('packages:'):
      self._packages_check_common_args(command, args)
      
    if command == 'version':
      return self._command_version()
    elif command == 'packages:update':
      return self._command_packages_update(args.root_dir,
                                           args.wipe,
                                           args.project_name,
                                           args.downgrade,
                                           args.force,
                                           args.dont_touch_update_script,
                                           args.build_target)
    elif command == 'packages:print':
      return self._command_packages_print(args.root_dir,
                                          args.project_name,
                                          args.build_target)
    elif command in [ 'config:packages' ]:
      return self._command_config_packages(args.root_dir, args.project_name, args.build_target)
    elif command in [ 'config:projects' ]:
      return self._command_config_projects(args.root_dir, args.build_target)
    else:
      raise RuntimeError('Unknown command: %s' % (command))
    return 0

  def _command_packages_install(self, dest_dir, project_name, packages, wipe, bt):
    rm = manager(self.artifact_manager, bt, dest_dir)
    return self._update_project(rm, project_name, packages, wipe, bt)

  def _command_packages_print(self, root_dir, project_name, bt):
    rm = manager(self.artifact_manager, bt, root_dir)
    assert project_name
    packages = rm.installed_packages(project_name, bt)
    for p in packages:
      print(p)
    return 0

  def _command_config_packages(self, root_dir, project_name, bt):
    rm = manager(self.artifact_manager, bt, root_dir)
    config = rm.config(bt)
    section = config.get(project_name, None)
    if not section:
      return 1
    packages = section.get('packages', None)
    if not packages:
      return 1
    for p in sorted(packages):
      print(p)
    return 0
  
  def _command_config_projects(self, root_dir, bt):
    rm = manager(self.artifact_manager, bt, root_dir)
    config = rm.config(bt)
    for project in sorted(config.keys()):
      print(project)
    return 0
  
  UPDATE_SCRIPT_TEMPLATE = '''#!/bin/bash
_root_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
retool.py packages update ${_root_dir} @STORAGE_CONFIG_FILENAME@ @ARTIFACTS_PROVIDER@  ${1+"$@"}
'''

  def _command_packages_update(self, root_dir, wipe, project_name, allow_downgrade,
                               force_install, dont_touch_update_script, bt):
    rm = manager(self.artifact_manager, bt, root_dir)
    success = rm.update_from_config(bt,
                                    wipe,
                                    project_name = project_name,
                                    allow_downgrade = allow_downgrade,
                                    force_install = force_install)
    if not dont_touch_update_script:
      update_script = manager_script(self.UPDATE_SCRIPT_TEMPLATE, 'update.sh')
      variables = {
        '@STORAGE_CONFIG_FILENAME@': self._storage_config_filename,
        '@ARTIFACTS_PROVIDER@': self._artifacts_provider,
      }
      update_script.save(root_dir, variables)
    return self.bool_to_exit_code(success)

  def _update_project(self, rm, project_name, packages, wipe, bt):
    if wipe:
      rm.wipe_project_dir(project_name, bt)
    success = rm.resolve_and_update_packages(project_name, packages, bt)
    return self.bool_to_exit_code(success)

  def bool_to_exit_code(clazz, success):
   if success:
     return 0
   else:
     return 1

  def _command_version(self):
    from bes.version import version_cli
    import rebuild
    vcli = version_cli(rebuild)
    vcli.version_print_version()
    return 0
   
  @classmethod
  def run(clazz):
    raise SystemExit(tool_cli().main())
