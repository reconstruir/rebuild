#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.common.check import check
from bes.system.log import log
from rebuild.base.build_system import build_system

from .ingest_cli_command import ingest_cli_command
from .ingest_cli_options import ingest_cli_options

class ingest_cli_args(object):

  def __init__(self):
    pass
  
  def ingest_add_args(self, subparser):
    default_systems = ingest_cli_options.DEFAULT_SYSTEMS
    default_cache_dir = ingest_cli_options.DEFAULT_CACHE_DIR
    
    p = subparser.add_parser('run', help = 'Run ingester on a project.')
    p.add_argument('--system', action = 'append', default = default_systems, type = str, dest = 'systems',
                   choices = tuple(build_system.SYSTEMS),
                   help = 'Systems to ingest for.  Can be given multiple times. [ {} ]'.format(', '.join(default_systems)))
    p.add_argument('--cache-dir', action = 'store', default = default_cache_dir, type = str,
                   help = 'The directory where downloads are cached. [ {} ]'.format(default_cache_dir))
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
#    p.add_argument('--username', action = 'store', default = None, type = str,
#                   help = 'The artifatory username. [ None ]')
#    p.add_argument('--password', action = 'store', default = None, type = str,
#                   help = 'The artifatory password. [ None ]')
#    p.add_argument('--tries', action = 'store', default = 1, type = int, dest = 'num_tries',
#                   help = 'The number of tries to publish. [ 1 ]')
    
  def _command_ingest_run(self, vfs_config, project_dir, args, systems, cache_dir,
                          include, exclude, dry_run, verbose):
    options = ingest_cli_options(dry_run = dry_run,
                                 verbose = verbose,
                                 systems = systems,
                                 cache_dir = cache_dir,
                                 exclude = exclude,
                                 include = include)
    return ingest_cli_command.run(vfs_config, project_dir, args, options)
