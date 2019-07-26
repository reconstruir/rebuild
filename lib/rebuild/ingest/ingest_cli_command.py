#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.url.http_download_cache import http_download_cache
from bes.git.git_archive_cache import git_archive_cache
from bes.system.log import logger

from bes.fs.fs.fs_registry import fs_registry
from bes.fs.fs.fs_local import fs_local
from bes.fs.temp_file import temp_file

from rebuild.ingest.ingest_file_parser import ingest_file_parser

class ingest_cli_command(object):
  'Implementations of the vault cli commands.'

  log = logger('ingest')
  
  @classmethod
  def run(clazz, project_file, fs_config_file, system, cache_dir, dry_run, verbose):
    'Run the ingestion process.'
    check.check_string(project_file)
    check.check_string(fs_config_file)
    check.check_string(system)
    check.check_bool(dry_run)
    check.check_bool(verbose)
    clazz.log.debug('run: project_file={} fs_config_file={}'.format(project_file, fs_config_file))

    project = ingest_file_parser.parse_file(project_file)
    clazz.log.debug('run: project variables={}'.format(project.variables))
    
    fs = fs_registry.load_from_config_file(fs_config_file)
    clazz.log.debug('run: fs={}'.format(fs))

    tmp_dir = temp_file.make_temp_dir()

    global_variables = project.variables.to_dict()
    
    for entry in project.entries:
      values = entry.resolve_method_values(system, global_variables).to_dict()
      clazz.log.debug('run: method={} entry={}:{}'.format(entry.method.descriptor.method(), entry.name, entry.version))
      for key, value in values.items():
        clazz.log.debug('run: {}: {}'.format(key, value))
      ingested_filename = values['ingested_filename']
      filename = entry.download(system, global_variables, cache_dir, tmp_dir)
      clazz.log.debug('run: uploading {} to {}'.format(filename, ingested_filename))
      fs.upload_file(ingested_filename, filename)
      
    return 0

  @classmethod
  def _make_http_cache(clazz):
    cache_dir = path.expanduser('~/.egoist/ingest/downloads/http')
    return http_download_cache(cache_dir)

  @classmethod
  def _make_git_cache(clazz):
    cache_dir = path.expanduser('~/.egoist/ingest/downloads/git')
    return git_archive_cache(cache_dir)
