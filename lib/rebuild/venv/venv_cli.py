#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, copy, os, os.path as path
from collections import namedtuple

from bes.system import log
from bes.archive import archiver
from bes.key_value import key_value_parser
from bes.system import host
from bes.fs import file_util, temp_file
from rebuild.base import build_arch, build_blurb, build_system, build_target, build_target_cli, build_level

from rebuild.config import storage_config_manager
from rebuild.package.artifact_manager_factory import artifact_manager_factory

from .venv_config import venv_config
from .venv_install_options import venv_install_options
from .venv_manager import venv_manager
from .venv_shell_script import venv_shell_script

# This is a hack to deal with the fact that storage_artifactory is a plugin
# but there is no system (yet) to load such plugins
from rebuild.storage.storage_artifactory import storage_artifactory
from rebuild.storage.storage_local import storage_local

class venv_cli(build_target_cli):

  def __init__(self):
    log.add_logging(self, 'venv')
    build_blurb.add_blurb(self, 'venv')
    self.parser = argparse.ArgumentParser()

    commands_subparser = self.parser.add_subparsers(help = 'commands', dest = 'command')

    # version
    version_parser = commands_subparser.add_parser('version', help = 'Version')
    
    # packages
    self.packages_parser = commands_subparser.add_parser('packages', help = 'Packages')
    self.packages_subparsers = self.packages_parser.add_subparsers(help = 'packages_commands', dest = 'subcommand')

    self.packages_subparsers.add_parser('update', help = 'Update installed packages')
    self.packages_subparsers.add_parser('print', help = 'Print installed packages')

    # packages:update
    update_parser = self.packages_subparsers.add_parser('update', help = 'Update packages')
    self._packages_add_common_args(update_parser)
    update_parser.add_argument('--wipe-first',
                               action = 'store_true',
                               default = False,
                               help = 'Wipe the installation dir first before updating [ False ]')
    update_parser.add_argument('--allow-downgrade',
                               action = 'store_true',
                               default = False,
                               help = 'Allow downgrade of packages [ False ]')
    update_parser.add_argument('--allow-same-version',
                               action = 'store_true',
                               default = False,
                               help = 'Allow same version reinstall if content changed [ False ]')
    update_parser.add_argument('--dont-touch-scripts',
                               action = 'store_true',
                               default = False,
                               help = 'Dont touch the update.sh scripts when done updating. [ False ]')
    update_parser.add_argument('project_name',
                               default = None,
                               nargs = '?',
                               help = 'Project name []')

    # packages:print
    print_parser = self.packages_subparsers.add_parser('print', help = 'Print packages')
    self._packages_add_common_args(print_parser)
    print_parser.add_argument('project_name',
                              default = None,
                              nargs = '?',
                              help = 'Project name [ None ]')
    print_parser.add_argument('--versions',
                              action = 'store_true',
                              default = False,
                              help = 'Include the package versions. [ False ]')

    # packages:clear
    clear_parser = self.packages_subparsers.add_parser('clear', help = 'Clear packages')
    self._packages_add_common_args(clear_parser)
    clear_parser.add_argument('project_name',
                               default = None,
                               nargs = '?',
                               help = 'Project name []')

    
    # config
    self.config_parser = commands_subparser.add_parser('config', help = 'Config')
    self.config_subparsers = self.config_parser.add_subparsers(help = 'config_commands', dest = 'subcommand')

    # config:packages
    packages_parser = self.config_subparsers.add_parser('packages', help = 'Print information about config packages.')
    self._packages_add_common_args(packages_parser)
    packages_parser.add_argument('project_name',
                                 default = None,
                                 nargs = '?',
                                 help = 'Project name []')

    # config:projects
    projects_parser = self.config_subparsers.add_parser('projects', help = 'Print information about config projects.')
    self._packages_add_common_args(projects_parser)

  def _packages_add_common_args(self, parser):
    'Add common arguments for all the "packages" command'
    self.build_target_add_arguments(parser)
    default_config = 'config/venvs_config.revenv'
    parser.add_argument('root_dir',
                        action = 'store',
                        default = None,
                        help = 'The root directory [ None ]')
    parser.add_argument('artifacts_config_name',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'The storage provider to use for artifacts. [ None ]')
    parser.add_argument('--config',
                        action = 'store',
                        default = default_config,
                        type = str,
                        help = 'Configuration file for venvs. [ %s ]' % (default_config))
    parser.add_argument('--verbose',
                        '-v',
                        action = 'store_true',
                        default = False,
                        help = 'Verbose debug spew [ False ]')
    parser.add_argument('--debug',
                        action = 'store_true',
                        default = False,
                        help = 'Turn on debug logs [ False ]')
    parser.add_argument('--no-network',
                        action = 'store_true',
                        default = False,
                        help = 'Dont do any network.  Use local caches only. [ False ]')
    
  def _packages_check_common_args(self, command, args):
    'Add common arguments for all the "packages" commands.'
    self.log_d('command=%s; args=%s' % (command, str(args)))
    
    if not path.isabs(args.config):
      if not path.isfile(args.config):
        args.config = path.join(args.root_dir, args.config)

    if not path.isfile(args.config):
      raise IOError('%s: config file not found: %s' % (command, args.config))

    self._config_filename = args.config
    self._root_dir = args.root_dir
    self._artifacts_config_name = args.artifacts_config_name
    self._build_target = self.build_target_resolve(args)

    self.log_d('config: root_dir=%s' % (self._root_dir))
    self.log_d('config: config_filename=%s' % (self._config_filename))
    self.log_d('config: artifacts_config_name=%s' % (self._artifacts_config_name))
    self.log_d('config: build_target=%s' % (str(self._build_target)))
    
    self._config = venv_config.load(self._config_filename, self._build_target)

    storage_config = self._config.storage_config

    config = storage_config.get(self._artifacts_config_name)
    if not config:
      msg = 'config \"%s\" not found in %s\npossible configs: %s' % (self._artifacts_config_name,
                                                                     self._config.filename,
                                                                     ' '.join(storage_config.available_configs()))
      raise RuntimeError(msg)

    self.log_d('config=%s' % (str(config)))
    self._local_storage_cache_dir = path.join(self._root_dir, '.cache', 'storage')
    self.log_d('_local_storage_cache_dir=%s' % (self._local_storage_cache_dir))
    
    factory_config = artifact_manager_factory.config(self._local_storage_cache_dir, 'artifacts', args.no_network, config)
    self.log_d('factory_config=%s' % (str(factory_config)))
    self._artifact_manager = artifact_manager_factory.create(factory_config)
    self._artifact_manager = artifact_manager_factory.create(factory_config)
    self.log_d('artifact_manager=%s' % (str(self._artifact_manager)))
    self._manager = venv_manager(self._config, self._artifact_manager, self._build_target, self._root_dir)

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
    self.debug = getattr(args, 'debug', False)

    build_blurb.set_process_name('venv')
    build_blurb.set_verbose(self.verbose)

    if self.debug:
      log.configure('venv*=debug format=brief')

    if command == 'version':
      return self._command_version()
      
    self._packages_check_common_args(command, args)
      
    if command == 'packages:update':
      options = venv_install_options(allow_downgrade = args.allow_downgrade,
                                     allow_same_version = args.allow_same_version,
                                     wipe_first = args.wipe_first,
                                     dont_touch_scripts = args.dont_touch_scripts)
      return self._command_packages_update(args.project_name, options)
    elif command == 'packages:print':
      return self._command_packages_print(args.project_name, args.versions)
    elif command == 'packages:clear':
      return self._command_packages_clear(args.project_name)
    elif command == 'config:packages':
      return self._command_config_packages(args.project_name)
    elif command == 'config:projects':
      return self._command_config_projects()
    else:
      raise RuntimeError('Unknown command: %s' % (command))
    return 0

  def _command_packages_update(self, project_name, options):
    self.log_d('packages_update: project_name=%s; options=%s' % (project_name, options))
    if not self._verify_project_names([ project_name ]):
      return 1
    success = self._manager.update_from_config(project_name, self._build_target, options)
    if not options.dont_touch_scripts:
      update_script = venv_shell_script(self.UPDATE_SCRIPT_TEMPLATE, 'update.sh')
      variables = {
        '@CONFIG_FILENAME@': self._config_filename,
        '@ARTIFACTS_CONFIG_NAME@': self._artifacts_config_name,
      }
      update_script.save(self._root_dir, variables)
    return self.bool_to_exit_code(success)

  def _verify_project_names(self, project_names):
    available_projects = set(self._config.project_names())
    if not project_names:
      self.blurb('Please give a project name.  Available projects:')
      self.blurb(' '.join(self._config.project_names()), fit = True)
      return False
    for project_name in project_names:
      if project_name not in available_projects:
        self.blurb('No such project: %s.  Available projects:' % (project_name))
        self.blurb(' '.join(self._config.project_names()), fit = True)
        return False
    return True
  
  def _command_packages_print(self, project_name, include_version):
    if not self._verify_project_names([ project_name ]):
      return 1
    packages = self._manager.installed_packages_names(project_name, self._build_target, include_version = include_version)
    for p in packages:
      print(p)
    return 0

  def _command_packages_clear(self, project_name):
    if not self._verify_project_names([ project_name ]):
      return 1
    self._manager.clear_project_from_config(project_name, self._build_target)
    return 0

  def _command_config_packages(self, project_name):
    if not self._verify_project_names([ project_name ]):
      return 1
    packages = self._config.package_names(project_name, self._build_target)
    for p in sorted(packages):
      print(p)
    return 0

  def _command_config_projects(self):
    projects = self._config.project_names()
    for p in sorted(projects):
      print(p)
    return 0
  
  UPDATE_SCRIPT_TEMPLATE = '''#!/bin/bash
_root_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
revenv.py packages update ${_root_dir} @ARTIFACTS_CONFIG_NAME@ ${1+"$@"} --config @CONFIG_FILENAME@ --allow-same-version
'''

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
    raise SystemExit(venv_cli().main())
