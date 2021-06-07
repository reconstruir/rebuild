# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, copy, os, os.path as path
from bes.system.log import log
from bes.build.build_blurb import build_blurb
from bes.version.version_cli import version_cli
from bes.system.log import log
from bes.common.check import check
from bes.cli.argparser_handler import argparser_handler

from rebuild.recipe.recipe_cli_args import recipe_cli_args

# needed for version_cli to work in standalone mode (pyinstaller)
import bes  # noqa

class retool_cli(
  recipe_cli_args,
):

  def __init__(self):
    log.add_logging(self, 'retool')
    build_blurb.add_blurb(self, 'retool')
    self.parser = argparse.ArgumentParser()

    commands_subparser = self.parser.add_subparsers(help='commands', dest='command_group')

    self.add_command_group(commands_subparser, 'recipe', 'recipe_add_args', 'Recipe manipulation')

    # version
    version_parser = commands_subparser.add_parser('version', help='Version a build to a build list.')
    version_cli.arg_sub_parser_add_arguments(version_parser)

  def _command_version(self, print_all, brief):
    version_cli.print_everything(
      'rebuild',
      dependencies = ['bes'],
      brief = brief,
      print_all = print_all
    )
    return 0

  def main(self):
    return argparser_handler.main('retool', self.parser, self)

  def add_command_group(self, commands_subparser, command_group, arg_adder, help_blurb):
    parser = commands_subparser.add_parser(command_group, help=help_blurb)
    subparsers_help_blurb = '%s_commands' % (command_group)
    subparsers = parser.add_subparsers(help=subparsers_help_blurb, dest='command')
    adder = getattr(self, arg_adder)
    adder(subparsers)

  @classmethod
  def run(clazz):
    raise SystemExit(retool_cli().main())
