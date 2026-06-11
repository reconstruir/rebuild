#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler

from .ingest_cli_command import ingest_cli_command
from .ingest_cli_options import ingest_cli_options

class ingest_command_handler(bcli_command_handler):

  def name(self):
    return 'ingest'

  def _command_run(self, vfs_config, project_dir, args, systems, cache_dir, include, exclude,
                   dry_run, verbose, options):
    run_options = ingest_cli_options(dry_run = dry_run,
                                     verbose = verbose,
                                     systems = systems,
                                     cache_dir = cache_dir,
                                     exclude = exclude or None,
                                     include = include or None)
    return ingest_cli_command.run(vfs_config, project_dir, args, run_options)
