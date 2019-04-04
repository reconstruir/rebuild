#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.compat import StringIO
from bes.common import check, cached_property, tuple_util
from bes.fs import file_util

class storage_address(namedtuple('storage_address', 'hostname, repo, root_dir, sub_repo, filename')):

  def __new__(clazz, hostname, repo, root_dir, sub_repo, filename):
    check.check_string(hostname)
    hostname = clazz._normalize_hostname(hostname)
    check.check_string(repo)
    repo = clazz._normalize_path(repo)
    if root_dir:
      root_dir = clazz._normalize_path(root_dir)
    if sub_repo is not None:
      check.check_string(sub_repo)
      sub_repo = clazz._normalize_path(sub_repo)
    if filename is not None:
      check.check_string(filename)
      filename = clazz._normalize_path(filename)
    return clazz.__bases__[0].__new__(clazz, hostname, repo, root_dir, sub_repo, filename)

  @classmethod
  def _normalize_hostname(clazz, hostname):
    if not hostname.endswith('/'):
      return hostname + '/'
    return hostname
  
  @classmethod
  def _normalize_path(clazz, filename):
    return file_util.strip_sep(filename)
  
  def __str__(self):
    return self.url

  @cached_property
  def url(self):
    buf = StringIO()
    buf.write(self.hostname)
    buf.write(self.repo)
    if self.root_dir:
      buf.write('/')
      buf.write(self.root_dir)
    if self.sub_repo:
      buf.write('/')
      buf.write(self.sub_repo)
    if self.filename:
      buf.write('/')
      buf.write(self.filename)
    return buf.getvalue()

  @cached_property
  def file_folder(self):
    'Return the folder for self.filename'
    return '{repo}/{root_dir}/{sub_repo}'.format(repo = self.repo, root_dir = self.root_dir, sub_repo = self.sub_repo)

  @cached_property
  def file_path(self):
    'Return the full path for self.filename or raise an error if filename is None'
    if not self.filename:
      raise ValueError('no filename available')
    return '{file_folder}/{filename}'.format(file_folder = self.file_folder, filename = self.filename)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  def mutate_filename(self, filename):
    return self.clone({ 'filename': filename })
  
    
check.register_class(storage_address)
