#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from os import path

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.fs.temp_file import temp_file
from bes.system.log import logger

from .ingest_project import ingest_project
from .ingest_error import ingest_error

class ingest_runner(object):
  'Main class that runs ingestion.'

  log = logger('ingest')
  
  def __init__(self, fs, base_dir, args = []):
    check.check_vfs_fs(fs)
    self._fs = fs
    self._project = ingest_project(base_dir, args = args)

  @property
  def project(self):
    return self._project
    
  def load(self):
    self._project.load()

  def check_has_entry(self, entry_name):
    check.check_string(entry_name)
    if self.project.has_entry(entry_name):
      return
    entry_names = ' '.join(self.project.entry_names)
    msg = 'No such entry found: {} - should be on of: {}'.format(entry_name, entry_names)
    raise ingest_error(msg)
    
  def ingest_one(self, entry_name, options):
    check.check_string(entry_name)
    check.check_ingest_cli_options(options)
    
    entry = self._project.find_entry(entry_name)
    tmp_dir = self._tmp_dir
    system = options.systems[0]

    self.log.debug('_ingest_one_entry: entry={} fs={} system={}'.format(entry.name, self._fs, system))
    
    global_variables = entry.ingest_file.variables.to_dict()
    values = entry.resolve_method_values(system, global_variables).to_dict()
    self.log.debug('run: method={} entry={}:{}'.format(entry.method.descriptor.method(), entry.name, entry.version))
    for key, value in values.items():
      self.log.debug('run: {}: {}'.format(key, value))
    remote_filename = values['ingested_filename']
    local_filename = entry.download(system, global_variables, options.cache_dir, tmp_dir)
    self.log.debug('run: uploading {} to {}'.format(local_filename, remote_filename))
    self._fs.upload_file(local_filename, remote_filename)

  def ingest_all(self, options):
    check.check_ingest_cli_options(options)
    for entry_name in self.project.entry_names:
      self.ingest_one(entry_name, options)
    
  @cached_property
  def _tmp_dir(self):
    return temp_file.make_temp_dir()
  
#  @classmethod
#  def _make_http_cache(clazz):
#    cache_dir = path.expanduser('~/.egoist/ingest/downloads/http')
#    return http_download_cache(cache_dir)
#
#  @classmethod
#  def _make_git_cache(clazz):
#    cache_dir = path.expanduser('~/.egoist/ingest/downloads/git')
#    return git_archive_cache(cache_dir)
