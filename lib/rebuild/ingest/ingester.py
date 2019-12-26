#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from os import path

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.fs.temp_file import temp_file

#from bes.url.http_download_cache import http_download_cache
#from bes.git.git_archive_cache import git_archive_cache
#from bes.system.log import logger

#from bes.vfs.vfs_registry import vfs_registry
#from bes.vfs.vfs_local import vfs_local

#from rebuild.ingest.ingest_file_parser import ingest_file_parser

class ingester(object):
  'Main class that drives ingestion.'

  log = logger('ingester')
  
  def __init__(clazz, project):
    check.check_ingest_file(project)

    self._project = project
#    self._fs = fs
    self._global_variables = self._project.variables.to_dict()
    
    clazz.log.debug('ingester: project={}'.format(project, fs, cache_dir))

  def run_all(self, entry_name):
    tmp_dir = self._tmp_dir
    if entry_name:
      for entry in project.entries:
        if entry.name == entry_name:
          clazz._ingest_one_entry(entry, system, global_variables, cache_dir, tmp_dir, fs, dry_run, verbose)
          return 0
      
    
    for entry in project.entries:
      clazz._ingest_one_entry(entry, system, global_variables, cache_dir, tmp_dir, fs, dry_run, verbose)
      
    return 0

  def run_one(self, entry_name):
    check.check_string(entry_name)
    tmp_dir = self._tmp_dir
    if entry_name:
      for entry in project.entries:
        if entry.name == entry_name:
          clazz._ingest_one_entry(entry, system, global_variables, cache_dir, tmp_dir, fs, dry_run, verbose)
          return 0
      
    
    for entry in project.entries:
      clazz._ingest_one_entry(entry, system, global_variables, cache_dir, tmp_dir, fs, dry_run, verbose)
      
    return 0
  
  @cached_property
  def _tmp_dir(self):
    return temp_file.make_temp_dir()
  
  def _ingest_one_entry(self, entry, system, global_variables, cache_dir, tmp_dir, fs, dry_run, verbose):
    clazz.log.debug('_ingest_one_entry: entry={} fs={}'.format(entry.name, fs))

    values = entry.resolve_method_values(system, global_variables).to_dict()
    clazz.log.debug('run: method={} entry={}:{}'.format(entry.method.descriptor.method(), entry.name, entry.version))
    for key, value in values.items():
      clazz.log.debug('run: {}: {}'.format(key, value))
    remote_filename = values['ingested_filename']
    local_filename = entry.download(system, global_variables, cache_dir, tmp_dir)
    clazz.log.debug('run: uploading {} to {}'.format(local_filename, remote_filename))
    fs.upload_file(local_filename, remote_filename)
  
  @classmethod
  def _make_http_cache(clazz):
    cache_dir = path.expanduser('~/.egoist/ingest/downloads/http')
    return http_download_cache(cache_dir)

  @classmethod
  def _make_git_cache(clazz):
    cache_dir = path.expanduser('~/.egoist/ingest/downloads/git')
    return git_archive_cache(cache_dir)
