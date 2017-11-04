#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import argparse, copy, os, os.path as path
from collections import namedtuple

from bes.archive import archiver
from bes.key_value import key_value_parser
from bes.system import host
from bes.fs import file_util, temp_file
from rebuild.base import build_arch, build_blurb, build_system, build_target, build_type
from rebuild.packager import rebuild_manager
from rebuild.package_manager import artifact_manager, Package, package_tester
from rebuild.tools_manager import tools_manager
from .rebuild_manager_script import rebuild_manager_script

class rebuild_manager_cli(object):

  TOOLS = 'tools'
  UPDATE = 'update'

  DEFAULT_ROOT_DIR = path.expanduser('~/.rebuild')
  
  def __init__(self):
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
                                help = 'Wipe the installation dir before installing [ False ]')
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
    self.package_parser = self.commands_subparser.add_parser('package', help = 'Package')
    self.package_subparsers = self.package_parser.add_subparsers(help = 'package_commands', dest = 'subcommand')

    # package.files
    package_files_parser = self.package_subparsers.add_parser('files', help = 'List files in package')
    package_files_parser.add_argument('package', action = 'store', help = 'Package to list files for')

    # package.info
    package_info_parser = self.package_subparsers.add_parser('info', help = 'List info in package')
    package_info_parser.add_argument('package', action = 'store', help = 'Package to list info for')

    # package.metadata
    package_metadata_parser = self.package_subparsers.add_parser('metadata', help = 'List metadata in package')
    package_metadata_parser.add_argument('package', action = 'store', help = 'Package to list metadata for')
    
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
    self.test_parser.add_argument('-o', '--opts', action = 'store', type = str, default = '')
    self.test_parser.add_argument('-v', '--verbose', action = 'store_true')
    self.test_parser.add_argument('-b', '--build-type', action = 'store', type = str, default = build_target.DEFAULT, help = 'Build type.  One of (%s) [ %s ]' % (','.join(build_type.BUILD_TYPES), build_type.DEFAULT_BUILD_TYPE))
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
    parser.add_argument('--build-type',
                        '-b',
                        action = 'store',
                        default = build_type.RELEASE,
                        help = 'The system [ %s ]' % (build_type.RELEASE))
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
  def _packages_check_common_args(self, args):
    'Add common arguments for all the "packages" command'
    if args.artifacts:
      if not path.isdir(args.artifacts):
        raise RuntimeError('Not an artifacts directory: %s' % (args.artifacts))
    args.artifact_manager = artifact_manager(args.artifacts, address = None, no_git = True)
    args.build_target = self._validate_build_target(args)
    
  def main(self):
    args = self.parser.parse_args()
    subcommand = getattr(args, 'subcommand', None)
    if subcommand:
      command = '%s:%s' % (args.command, subcommand)
    else:
      command = args.command
      
    if command == 'tools:update':
      return self.__command_tools_update()
    elif command == 'tools:install':
      return self.__command_tools_install(args.dest_dir)
    elif command == 'tools:print':
      return self.__command_tools_print()
    elif command in [ 'packages:install', 'packages:update' ]:
      self._packages_check_common_args(args)
      if command == 'packages:install':
        return self.__command_packages_install(args.artifact_manager,
                                               args.dest_dir,
                                               args.project_name,
                                               args.packages,
                                               args.wipe,
                                               args.build_target)
      elif command == 'packages:update':
        return self.__command_packages_update(args.artifact_manager,
                                              args.root_dir,
                                              args.wipe,
                                              args.project_name,
                                              args.downgrade,
                                              args.build_target)
    elif command in [ 'packages:uninstall' ]:
      return self.__command_packages_uninstall(args.dest_dir,
                                               args.project_name,
                                               args.packages,
                                               self._validate_build_target(args))
    elif command in [ 'packages:print' ]:
      return self.__command_packages_print(args.root_dir,
                                           args.project_name,
                                           self._validate_build_target(args))
    elif command in [ 'config:packages' ]:
      bt = self._validate_build_target(args)
      return self.__command_config_packages(args.root_dir, args.project_name, bt)
    elif command == 'package:files':
      return self.__command_package_files(args.package)
    elif command == 'package:info':
      return self.__command_package_info(args.package)
    elif command == 'package:metadata':
      return self.__command_package_metadata(args.package)
    elif command == 'test':
      return self.__command_test(args.build_type, args.package_tarball, args.test,
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
    if not args.build_type in build_type.BUILD_TYPES:
      return ( None, 'Invalid build_type: %s' % (args.build_type) )
    return ( build_target(system, args.build_type), None )

  @classmethod
  def _validate_build_target(clazz, args):
    bt, error_message = clazz._parse_build_target(args)
    if not bt:
      print(error_message)
      raise SystemExit(1)
    return bt

  def __command_tools_update(self):
    print("__command_tools_update()")
    return 0

  def __command_tools_print(self):
    print("__command_tools_print()")
    return 0

  def __command_tools_install(self, dest_dir):
    assert False, 'implement me properly'
    am = artifact_manager(None, rebuild_manager.ARTIFACTS_GIT_ADDRESS)
    rebbe = rebuild_manager(dest_dir)
    return 0

  def __command_packages_install(self, artifact_manager, dest_dir, project_name, packages, wipe, bt):
    rebbe = rebuild_manager(dest_dir, artifact_manager = artifact_manager)
    return self.__update_project(rebbe, project_name, packages, wipe, bt)

  def __command_packages_uninstall(self, dest_dir, project_name, packages, bt):
    rebbe = rebuild_manager(dest_dir, artifact_manager = None)
    success = rebbe.uninstall_packages(project_name, packages, bt)
    return self.bool_to_exit_code(success)

  def __command_packages_print(self, root_dir, project_name, bt):
    rebbe = rebuild_manager(root_dir, artifact_manager = None)
    assert project_name
    packages = rebbe.installed_packages(project_name, bt)
    for p in packages:
      print(p)
    return 0

  def __command_config_packages(self, root_dir, project_name, bt):
    rebbe = rebuild_manager(root_dir, artifact_manager = None)
    config = rebbe.config(bt)
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
rebuild_manager.py packages update --artifacts @ARTIFACTS_DIR@ --root-dir @ROOT_DIR@ ${1+"$@"}
'''

  def __command_packages_update(self, artifact_manager, root_dir, wipe, project_name, allow_downgrade, bt):
    rebbe = rebuild_manager(root_dir, artifact_manager = artifact_manager)
    success = rebbe.update_from_config(bt, project_name = project_name, allow_downgrade = allow_downgrade)
    update_script = rebuild_manager_script(self.UPDATE_SCRIPT_TEMPLATE, 'update.sh')
    variables = {
      '@ARTIFACTS_DIR@': artifact_manager.publish_dir,
      '@ROOT_DIR@': root_dir,
    }
    update_script.save(root_dir, variables)
    return self.bool_to_exit_code(success)

  def __update_project(self, rebbe, project_name, packages, wipe, bt):
    if wipe:
      rebbe.wipe_project_dir(project_name)
    success = rebbe.resolve_and_update_packages(project_name, packages, bt)
    return self.bool_to_exit_code(success)

  def bool_to_exit_code(clazz, success):
   if success:
     return 0
   else:
     return 1

  def __command_package_files(self, tarball):
    package = Package(tarball)
    for f in package.files:
      print(f)
    return 0

  def __command_package_info(self, tarball):
    package = Package(tarball)
    package_info = package.info
    info = str(package_info)
    parts = info.split(';')
    for part in parts:
      print((part.strip()))
    return 0

  def __command_package_metadata(self, tarball):
    content = archiver.extract_member_to_string(tarball, Package.INFO_FILENAME)
    print(content)
    return 0

  def __command_test(self, bt, package_tarball, test, artifacts_dir, tools_dir, tmp_dir, opts, verbose):
    DEFAULT_OPTIONS = 'build_python=False'
    #opts = copy.deepcopy(DEFAULT_OPTIONS)
    parsed_opts = key_value_parser.parse_to_dict(opts)
    #opts.update(parsed_opts)
    opts = parsed_opts

    if 'build_type' in opts and bt == build_target.DEFAULT:
      bt == opts['build_type']
  
    bt = build_type.parse_build_type(bt)

    opts['build_type'] = bt

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

    target = build_target(opts.get('system', build_target.DEFAULT),
                          opts.get('build_target', build_target.DEFAULT),
                          opts.get('archs', build_target.DEFAULT))

    build_blurb.blurb('tester', ' build_target: %s' % (target))
    build_blurb.blurb('tester', '      tmp_dir: %s' % (tmp_dir))
    build_blurb.blurb('tester', 'artifacts_dir: %s' % (artifacts_dir))

    if not Package.package_is_valid(package_tarball):
      raise RuntimeError('Not a valid package: %s' % (package_tarball))
  
    test_dir = path.join(tmp_dir, 'test')
    source_dir = path.dirname(test)
    test_config = package_tester.test_config(package_tarball, source_dir, test_dir, am, tm, target)
    tester = package_tester(test_config, test)

    result = tester.run()

    if not result.success:
      print("result: ", result)
      return 1

    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(rebuild_manager_cli().main())
