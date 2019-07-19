#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check

from rebuild.ingest.ingest_file_parser import ingest_file_parser

class ingest_cli_command(object):
  'Implementations of the vault cli commands.'
  
  @classmethod
  def run(clazz, project_file, storage_config, dry_run, verbose):
    'Run the ingestion process.'
    check.check_string(project_file)
    check.check_string(storage_config)
    check.check_bool(dry_run)
    check.check_bool(verbose)

    project = ingest_file_parser.parse_file(project_file)

    for entry in project.entries:
      print(entry)
    
    return 0
