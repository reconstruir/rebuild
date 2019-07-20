#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.url.http_download_cache import http_download_cache
from bes.git.git_archive_cache import git_archive_cache

from rebuild.ingest.ingest_file_parser import ingest_file_parser

class ingest_cli_command(object):
  'Implementations of the vault cli commands.'
  
  @classmethod
  def run(clazz, project_file, storage_config, system, cache_dir, dry_run, verbose):
    'Run the ingestion process.'
    check.check_string(project_file)
    check.check_string(storage_config)
    check.check_string(system)
    check.check_bool(dry_run)
    check.check_bool(verbose)

    project = ingest_file_parser.parse_file(project_file)

@    http_cache = clazz._make_http_cache()
#    git_cache = clazz._make_git_cache()
    
    for entry in project.entries:
      values = entry.resolve_method_values(system)
      print('{} {}'.format(entry.name, entry.version))
      for kv in values:
        print('  method: {}'.format(entry.method.descriptor.method()))
        print('  {}: {}'.format(kv.key, kv.value))
      print('\n')
      
    return 0

  @classmethod
  def _make_http_cache(clazz):
    cache_dir = path.expanduser('~/.egoist/ingest/downloads/http')
    return http_download_cache(cache_dir)

  @classmethod
  def _make_git_cache(clazz):
    cache_dir = path.expanduser('~/.egoist/ingest/downloads/git')
    return git_archive_cache(cache_dir)
