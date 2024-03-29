#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, copy, os, os.path as path
from collections import namedtuple

from bes.system import log
from bes.archive import archiver
from bes.key_value import key_value_parser
from bes.system import host
from bes.fs import file_util, temp_file
from rebuild.base import build_arch, build_blurb, build_system, build_target, build_level
from rebuild.package import artifact_manager, package, package_tester
from rebuild.tools_manager import tools_manager

from .manager import manager
from .manager_script import manager_script

class manager_cli(object):

  TOOLS = 'tools'
  UPDATE = 'update'

  DEFAULT_ROOT_DIR = path.expanduser('~/.rebuild')
  
  def __init__(self):
    log.add_logging(self, 'remanage')
    self.parser = argparse.ArgumentParser()
    self.commands_subparser = self.parser.add_subparsers(help = 'commands',
                                                         dest = 'command')
    # A tool command
    self.tools_parser = self.commands_subparser.add_parser('tools', help = 'Tools')
    self.tools_subparsers = self.tools_parser.add_subparsers(help = 'tools_commands', dest = 'subcommand')

    self.tools_subparsers.add_parser('update', help = 'Update installed tools')
    self.tools_subparsers.add_parser('print', help = 'Print installed tools')
    install_parser = self.tools_subparsers.add_parser('install', help = 'Install tools')
    install_parser.add_argument('dest_dir',
                                action = 'store',
                                default = None,
                                help = 'Destination directory [ cwd ]')


    # packages
    self.packages_parser = self.commands_subparser.add_parser('packages', help = 'Packages')
    self.packages_subparsers = self.packages_parser.add_subparsers(help = 'packages_commands', dest = 'subcommand')

    self.packages_subparsers.add_parser('update', help = 'Update installed packages')
    self.packages_subparsers.add_parser('print', help = 'Print installed packages')

    # packages.install
    install_parser = self.packages_subparsers.add_parser('install', help = 'Install packages')
    self._packages_add_common_args(install_parser)
    install_parser.add_argument('--wipe',
                                '-w',
                                action = 'store_true',
                                default = False,
                                help = 'Wipe the stuff dir before installing [ False ]')
    install_parser.add_argument('dest_dir',
                                action = 'store',
                                default = None,
                                help = 'Destination directory [ None ]')
    install_parser.add_argument('project_name',
                                action = 'store',
                                default = None,
                                help = 'Name of project [ None ]')
    install_parser.add_argument('packages',
                                action = 'store',
                                default = None,
                                nargs = '+',
                                help = 'Packages to install [ None ]')

    # packages.uninstall
    uninstall_parser = self.packages_subparsers.add_parser('uninstall', help = 'Uninstall packages')
    self._packages_add_common_args(uninstall_parser)

    uninstall_parser.add_argument('dest_dir',
                                action = 'store',
                                default = None,
                                help = 'Destination directory [ None ]')
    uninstall_parser.add_argument('project_name',
                                action = 'store',
                                default = None,
                                help = 'Name of project [ None ]')
    uninstall_parser.add_argument('packages',
                                action = 'store',
                                default = None,
                                nargs = '+',
                                help = 'Packages to uninstall [ None ]')

    # packages.update
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
    
    # packages.print
    print_parser = self.packages_subparsers.add_parser('print', help = 'Print packages')
    self._packages_add_common_args(print_parser)
    print_parser.add_argument('project_name',
                              action = 'store',
                              default = None,
                              nargs='?',
                              help = 'Project name [ None ]')

    # package
    self.package_parser = self.commands_subparser.add_parser('package', help = 'package')
    self.package_subparsers = self.package_parser.add_subparsers(help = 'package_commands', dest = 'subcommand')

    # package.files
    package_files_parser = self.package_subparsers.add_parser('files', help = 'List files in package')
    package_files_parser.add_argument('package', action = 'store', help = 'package to list files for')

    # package.info
    package_info_parser = self.package_subparsers.add_parser('info', help = 'List info in package')
    package_info_parser.add_argument('package', action = 'store', help = 'package to list info for')

    # package.metadata
    package_metadata_parser = self.package_subparsers.add_parser('metadata', help = 'List metadata in package')
    package_metadata_parser.add_argument('package', action = 'store', help = 'package to list metadata for')
    
    # config
    self.config_parser = self.commands_subparser.add_parser('config', help = 'Config')
    self.config_subparsers = self.config_parser.add_subparsers(help = 'config_commands', dest = 'subcommand')

    self.config_subparsers.add_parser('packages', help = 'Print config packages')

    # config.packages
    packages_parser = self.config_subparsers.add_parser('packages', help = 'Packages config')
    self._packages_add_common_args(packages_parser)
    packages_parser.add_argument('project_name',
                                 action = 'store',
                                 default = None,
                                 help = 'Name of project [ None ]')

    # test
    self.test_parser = self.commands_subparser.add_parser('test', help = 'Test')
    self.test_parser.add_argument('-v', '--verbose', action = 'store_true')
    self.test_parser.add_argument('-l', '--level', action = 'store', type = str, default = 'release',
                                  help = 'Build level.  One of (%s) [ release ]' % (','.join(build_level.LEVELS)))
    self.test_parser.add_argument('--tmp-dir', action = 'store', default = None,
                                  help = 'Temporary directory to use or a random one if not given. [ None ]')
    self.test_parser.add_argument('artifacts_dir', action = 'store', default = None, type = str,
                                  help = 'The place to locate artifacts [ ~/artifacts ]')
    self.test_parser.add_argument('tools_dir', action = 'store', default = None, type = str,
                                  help = 'The place to locate tools [ ~/tools ]')
    self.test_parser.add_argument('package_tarball', action = 'store', default = None, type = str,
                                  help = 'The tarball of the package to test [ None ]')
    self.test_parser.add_argument('test', action = 'store', type = str,
                                  help = 'The test(s) to run [ None ]')

  def _packages_add_common_args(self, parser):
    'Add common arguments for all the "packages" command'
    parser.add_argument('--verbose',
                        '-v',
                        action = 'store_true',
                        default = False,
                        help = 'Verbose debug spew [ False ]')
    parser.add_argument('--system',
                        '-s',
                        action = 'store',
                        default = host.SYSTEM,
                        help = 'The system [ %s ]' % (host.SYSTEM))
    parser.add_argument('--level',
                        '-l',
                        action = 'store',
                        default = build_level.RELEASE,
                        help = 'The build level [ %s ]' % (build_level.RELEASE))
    parser.add_argument('--artifacts',
                        '-a',
                        action = 'store',
                        default = None,
                        help = 'The place to locate artifacts [ None ]')
    parser.add_argument('--root-dir',
                        '-r',
                        action = 'store',
                        default = self.DEFAULT_ROOT_DIR,
                        help = 'The root directory [ %s ]' % (self.DEFAULT_ROOT_DIR))
    parser.add_argument('--distro',
                        '-d',
                        action = 'store',
                        default = None,
                        help = 'The distro [ None ]')
  def _packages_check_common_args(self, args):
    'Add common arguments for all the "packages" command'
    if args.artifacts:
      if not path.isdir(args.artifacts):
        raise RuntimeError('Not an artifacts directory: %s' % (args.artifacts))
    args.build_target = self._validate_build_target(args)
    
  def main(self):
    args = self.parser.parse_args()
    subcommand = getattr(args, 'subcommand', None)
    if subcommand:
      command = '%s:%s' % (args.command, subcommand)
    else:
      command = args.command

    if hasattr(args, 'artifacts'):
      self.artifact_manager = artifact_manager(args.artifacts, address = None, no_git = True)
    else:
      self.artifact_manager = artifact_manager(None)

    self.verbose = getattr(args, 'verbose', False)

    if self.verbose:
      log.configure('remanage*=info format=brief width=20')
      
    if command == 'tools:update':
      return self._command_tools_update()
    elif command == 'tools:install':
      return self._command_tools_install(args.dest_dir)
    elif command == 'tools:print':
      return self._command_tools_print()
    elif command in [ 'packages:install', 'packages:update' ]:
      self._packages_check_common_args(args)
      if command == 'packages:install':
        return self._command_packages_install(args.dest_dir,
                                              args.project_name,
                                              args.packages,
                                              args.wipe,
                                              args.build_target)
      elif command == 'packages:update':
        return self._command_packages_update(args.root_dir,
                                             args.wipe,
                                             args.project_name,
                                             args.downgrade,
                                             args.force,
                                             args.dont_touch_update_script,
                                             args.build_target)
    elif command in [ 'packages:uninstall' ]:
      return self._command_packages_uninstall(args.dest_dir,
                                              args.project_name,
                                              args.packages,
                                              self._validate_build_target(args))
    elif command in [ 'packages:print' ]:
      return self._command_packages_print(args.root_dir,
                                          args.project_name,
                                          self._validate_build_target(args))
    elif command in [ 'config:packages' ]:
      bt = self._validate_build_target(args)
      return self._command_config_packages(args.root_dir, args.project_name, bt)
    elif command == 'package:files':
      return self._command_package_files(args.package)
    elif command == 'package:info':
      return self._command_package_info(args.package)
    elif command == 'package:metadata':
      return self._command_package_metadata(args.package)
    elif command == 'test':
      return self._command_test(args.level, args.package_tarball, args.test,
                                args.artifacts_dir, args.tools_dir,
                                args.tmp_dir, args.opts, args.verbose)
    else:
      raise RuntimeError('Unknown command: %s' % (command))
    return 0

  @classmethod
  def _parse_build_target(clazz, args):
    system = build_system.parse_system(args.system)
    if not system in build_system.SYSTEMS:
      return ( None, 'Invalid system: %s' % (args.system) )
    if not args.level in build_level.LEVELS:
      return ( None, 'Invalid build_level: %s' % (args.level) )
    if system == 'linux':
      distro = 'ubuntu'
      distro_version = '18'
    else:
      distro = ''
      distro_version = '10.10'
    return ( build_target(system, distro, distro_version, 'x86_64', args.level), None )

  @classmethod
  def _validate_build_target(clazz, args):
    bt, error_message = clazz._parse_build_target(args)
    if not bt:
      print(error_message)
      raise SystemExit(1)
    return bt

  def _command_tools_update(self):
    print("_command_tools_update()")
    return 0

  def _command_tools_print(self):
    print("_command_tools_print()")
    return 0

  def _command_tools_install(self, dest_dir):
    assert False, 'implement me properly'
    #am = artifact_manager(None, manager.ARTIFACTS_GIT_ADDRESS)
    #rm = manager(am, dest_dir)
    return 0

  def _command_packages_install(self, dest_dir, project_name, packages, wipe, bt):
    rm = manager(self.artifact_manager, bt, dest_dir)
    return self._update_project(rm, project_name, packages, wipe, bt)

  def _command_packages_uninstall(self, dest_dir, project_name, packages, bt):
    rm = manager(self.artifact_manager, bt, dest_dir)
    success = rm.uninstall_packages(project_name, packages, bt)
    return self.bool_to_exit_code(success)

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
  
  UPDATE_SCRIPT_TEMPLATE = '''#!/bin/bash
_root_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
remanager.py packages update --artifacts @ARTIFACTS_DIR@ --root-dir ${_root_dir} --force ${1+"$@"}
'''

  def _command_packages_update(self, root_dir, wipe, project_name, allow_downgrade,
                               force_install, dont_touch_update_script, bt):
    print('root_dir: %s' % (root_dir))
    rm = manager(self.artifact_manager, bt, root_dir)
    success = rm.update_from_config(bt,
                                    wipe,
                                    project_name = project_name,
                                    allow_downgrade = allow_downgrade,
                                    force_install = force_install)
    if not dont_touch_update_script:
      update_script = manager_script(self.UPDATE_SCRIPT_TEMPLATE, 'update.sh')
      variables = {
        '@ARTIFACTS_DIR@': self.artifact_manager.root_dir,
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

  def _command_package_files(self, tarball):
    package = package(tarball)
    for f in package.files:
      print(f)
    return 0

  def _command_package_info(self, tarball):
    package = package(tarball)
    package_info = package.info
    info = str(package_info)
    parts = info.split(';')
    for part in parts:
      print((part.strip()))
    return 0

  def _command_package_metadata(self, tarball):
    content = archiver.extract_member_to_string(tarball, package.METADATA_FILENAME)
    print(content)
    return 0

  def _command_test(self, bt, package_tarball, test, artifacts_dir, tools_dir, tmp_dir, opts, verbose):
    parsed_opts = key_value_parser.parse_to_dict(opts)
    opts = parsed_opts

    if 'build_level' in opts and bt == build_target.DEFAULT:
      bt == opts['build_level']
  
    bt = build_level.parse_level(bt)

    opts['build_level'] = bt

    build_blurb.set_process_name('package_tester')
    build_blurb.set_verbose(bool(verbose))

    if not path.isfile(test):
      raise RuntimeError('Test not found: %s' % (test))
  
    tmp_dir = None
    if tmp_dir:
      tmp_dir = tmp_dir
    else:
      tmp_dir = temp_file.make_temp_dir(delete = False)
    file_util.mkdir(tmp_dir)

    if not path.isdir(artifacts_dir):
      raise RuntimeError('Not an artifacts directory: %s' % (artifacts_dir))

    if not path.isdir(tools_dir):
      raise RuntimeError('Not an tools directory: %s' % (tools_dir))

    am = artifact_manager(artifacts_dir, address = None, no_git = True)
    tm = tools_manager(tools_dir)

    # FIXME666
    target = build_target(opts.get('system', host.SYSTEM), '', '', ( 'x86_64' ), 'release')
    build_blurb.blurb('tester', ' build_target: %s' % (str(target)))
    build_blurb.blurb('tester', '      tmp_dir: %s' % (tmp_dir))
    build_blurb.blurb('tester', 'artifacts_dir: %s' % (artifacts_dir))

    if not package.is_package(package_tarball):
      raise RuntimeError('Not a valid package: %s' % (package_tarball))
  
    test_dir = path.join(tmp_dir, 'test')
    source_dir = path.dirname(test)
    #test_config = namedtuple('test_config', 'script,package_tarball,artifact_manager,tools_manager,extra_env')
    test_config = package_tester.test_config(None, package_tarball, am, tm, []) #     source_dir, test_dir, am, tm, target)
    tester = package_tester(test_config, test)

    result = tester.run()

    if not result.success:
      print("result: ", result)
      return 1

    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(manager_cli().main())
