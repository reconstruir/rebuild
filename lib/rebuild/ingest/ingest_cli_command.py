#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.system.log import logger

from bes.vfs.vfs_registry import vfs_registry

from .ingest_cli_options import ingest_cli_options
from .ingest_runner import ingest_runner

class ingest_cli_command(object):
  'Ingest cli command handlers.'

  log = logger('ingest')
  
  @classmethod
  def run(clazz, vfs_config_file, project_dir, args, options):
    'Run the ingestion process.'
    check.check_string(vfs_config_file)
    check.check_string(project_dir)
    check.check_string_seq(args)
    check.check_ingest_cli_options(options)

    clazz.log.debug('run: vfs_config_file={}'.format(vfs_config_file))
    clazz.log.debug('run: project_dir={}'.format(project_dir))
    clazz.log.debug('run: args={}'.format(args))
    clazz.log.debug('run: options={}'.format(options))

    fs = vfs_registry.load_from_config_file(vfs_config_file)
    clazz.log.debug('run: fs={}'.format(fs))

    runner = ingest_runner(fs, project_dir, args = args)
    project = runner.project
    
    runner.load()

    if options.include:
      for entry_name in options.include:
        runner.check_has_entry(entry_name)
      for entry_name in options.include:
        runner.ingest_one(entry_name, options)
      return 0
    
    if options.exclude:
      for entry_name in options.exclude:
        runner.check_has_entry(entry_name)
      entry_names = runner.project.entry_names
      entry_names = [ n for n in entry_names if n not in options.exclude ]
      runner.ingest_some(entry_names, options)
      return 0
        
    runner.ingest_all(options)
    
    return 0
