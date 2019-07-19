#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.common.check import check
from bes.system.log import log
from rebuild.base.build_system import build_system

from .ingest_cli_command import ingest_cli_command

class ingest_cli_args(object):

  def __init__(self):
    pass
  
  def ingest_add_args(self, subparser):
    default_system = build_system.HOST
    
    p = subparser.add_parser('run', help = 'Run ingestion for a ingestion project.')
    p.add_argument('project_file', action = 'store', default = None, type = str,
                   help = 'The ingest project file. [ None ]')
    p.add_argument('storage_config', action = 'store', default = None, type = str,
                   help = 'The storage config file. [ None ]')
    p.add_argument('--system', action = 'store', default = default_system, type = str,
                   choices = tuple(build_system.SYSTEMS),
                   help = 'The system to ingest for. [ None ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Do not ingest anything just print what would happen. [ False ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Print verbose information about what is happening. [ False ]')
#    p.add_argument('--username', action = 'store', default = None, type = str,
#                   help = 'The artifatory username. [ None ]')
#    p.add_argument('--password', action = 'store', default = None, type = str,
#                   help = 'The artifatory password. [ None ]')
#    p.add_argument('--tries', action = 'store', default = 1, type = int, dest = 'num_tries',
#                   help = 'The number of tries to publish. [ 1 ]')
    
  def _command_ingest_run(self, project_file, storage_config, system, dry_run, verbose):
    return ingest_cli_command.run(project_file, storage_config, system, dry_run, verbose)
