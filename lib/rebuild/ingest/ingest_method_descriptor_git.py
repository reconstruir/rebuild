#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.git.git_archive_cache import git_archive_cache

from .ingest_method_descriptor_base import ingest_method_descriptor_base
from .ingest_method_field import ingest_method_field

class ingest_method_descriptor_git(ingest_method_descriptor_base):
  
  #@abstractmethod
  def method(self):
    return 'git'

  #@abstractmethod
  def fields(self):
    return (
      ingest_method_field('address'),
      ingest_method_field('revision'),
      ingest_method_field('ingested_filename'),
    )
  
  #@abstractmethod
  def download(self, args):
    address = self._check_download_field(args, 'address')
    revision = self._check_download_field(args, 'revision')
    ingested_filename = self._check_download_field(args, 'ingested_filename')
    cache_dir = self._check_download_field(args, 'cache_dir')
    cache = git_archive_cache(cache_dir)
    return cache.get_tarball(address, revision)