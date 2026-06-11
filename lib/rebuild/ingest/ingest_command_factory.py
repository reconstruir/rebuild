#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base
from bes.build.build_system import build_system

from .ingest_cli_options import ingest_cli_options
from .ingest_command_handler import ingest_command_handler

class ingest_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'ingest'

  @classmethod
  def description(clazz):
    return 'Ingest operations'

  def options_class(self):
    return None

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    pass

  def add_commands(self, subparsers):
    default_systems = ingest_cli_options.DEFAULT_SYSTEMS
    default_cache_dir = ingest_cli_options.DEFAULT_CACHE_DIR

    p = subparsers.add_parser('run', help = 'Run ingester on a project.')
    p.add_argument('--system', action = 'append', default = default_systems, type = str,
                   dest = 'systems', choices = tuple(build_system.SYSTEMS),
                   help = 'Systems to ingest for. Can be given multiple times. [ {} ]'.format(
                     ', '.join(default_systems)))
    p.add_argument('--cache-dir', action = 'store', default = default_cache_dir, type = str,
                   help = 'The directory where downloads are cached. [ {} ]'.format(
                     default_cache_dir))
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Do not ingest anything just print what would happen. [ False ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Print verbose information about what is happening. [ False ]')
    p.add_argument('--include', action = 'append', default = [], type = str,
                   help = 'Run ingestion just for the given entry. [ None ]')
    p.add_argument('--exclude', action = 'append', default = [], type = str,
                   help = 'Skip the given entry. [ None ]')
    p.add_argument('vfs_config', action = 'store', default = None, type = str,
                   help = 'The storage config file. [ None ]')
    p.add_argument('project_dir', action = 'store', default = None, type = str,
                   help = 'The ingest project file. [ None ]')
    p.add_argument('args', action = 'store', default = [], type = str, nargs = '*',
                   help = 'Additional arguments for ingester. [ None ]')

  def handler_class(self):
    return ingest_command_handler

  def supported_platforms(self):
    return 'all'
