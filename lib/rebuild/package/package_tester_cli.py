#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, copy, os, os.path as path
from collections import namedtuple

from bes.system.log import log
from bes.key_value.key_value_parser import key_value_parser
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from rebuild.base.build_blurb import build_blurb
from rebuild.base.build_level import build_level
from rebuild.base.build_target import build_target
from rebuild.base.build_target_cli import build_target_cli
from rebuild.package.artifact_manager_local import artifact_manager_local
from rebuild.package.package import package
from rebuild.package.package_tester import package_tester

class package_tester_cli(build_target_cli):

  def __init__(self):
    log.add_logging(self, 'remanage')
    self.parser = argparse.ArgumentParser()
    commands_subparser = self.parser.add_subparsers(help = 'commands',
                                                    dest = 'command')
    # test
    self.test_parser = commands_subparser.add_parser('test', help = 'Test')
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

  def main(self):
    args = self.parser.parse_args()
    self.build_target = self.build_target_resolve(args)
    subcommand = getattr(args, 'subcommand', None)
    if subcommand:
      command = '%s:%s' % (args.command, subcommand)
    else:
      command = args.command

    self.verbose = getattr(args, 'verbose', False)

    if self.verbose:
      log.configure('remanage*=info format=brief width=20')
      
    if command == 'test':
      return self._command_test(args.level, args.package_tarball, args.test,
                                args.artifacts_dir, args.tools_dir,
                                args.tmp_dir, args.opts, args.verbose)
    else:
      raise RuntimeError('Unknown command: %s' % (command))
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

    am = artifact_manager_local(artifacts_dir)
    tm = tools_manager(tools_dir, self.build_target, am)

    build_blurb.blurb('tester', ' build_target: %s' % (str(self.build_target)))
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
    raise SystemExit(package_tester_cli().main())
