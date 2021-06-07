# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli import cli
from bes.cli.cli_command import cli_command
from bes.best_cli.best_cli import best_cli
  
from bes.common.check import check

class rebuild_cli(cli):
  
  def __init__(self):
    super(rebuild_cli, self).__init__('rebuild')

  #@abstractmethod
  def command_group_list(self):
    'Return a list of tool items for this cli.'
    from rebuild.ingest.ingest_cli_args import ingest_cli_args

    return best_cli.COMMAND_GROUPS + [
      cli_command('ingest', 'ingest_add_args', 'Ingest stuff', ingest_cli_args),
    ]

  from bes.cli.cli_version_cli_args import cli_version_cli_args
  cli_version_cli_args.version_module_name = 'rebuild'
  cli_version_cli_args.version_dependencies = [ 'bes' ]
  #@abstractmethod
  def command_list(self):
    'Return a list of commands for this cli.'
    from .rebuild_depends_cli_args import rebuild_depends_cli_args
    return best_cli.COMMANDS + [
      cli_command('depends', 'depends_add_args', 'Print dependency information', rebuild_depends_cli_args),
    ]
  
  @classmethod
  def run(clazz):
    raise SystemExit(rebuild_cli().main())
