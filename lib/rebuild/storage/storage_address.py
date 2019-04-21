#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.compat import StringIO
from bes.common import check, tuple_util
from bes.property.cached_property import cached_property
from bes.fs import file_util
from bes.compat.url_compat import urlparse

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
  def repo_filename(self):
    'Return the folder for self.filename'
    parts = [ self.repo, self.root_dir, self.sub_repo, self.filename ]
    parts = [ p for p in parts if p ]
    return '/'.join(parts)
  
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  def mutate_filename(self, filename):
    return self.clone({ 'filename': filename })

  @classmethod
  def parse_url(self, url, has_host_root = False):
    parts = urlparse(url)
    path_parts = parts.path.split('/')
    if path_parts[0] != '':
      raise ValueError('invalid url: {}'.format(url))
    path_parts.pop(0)
    if has_host_root:
      if not path_parts:
        raise ValueError('url does not have a host_root: {}'.format(url))
      host_root = path_parts.pop(0)
    else:
      host_root = None
    hostname = '{scheme}://{netloc}'.format(**parts._asdict())
    if host_root:
      hostname = hostname + '/' + host_root
    if not path_parts:
      raise ValueError('url does not have a repo: {}'.format(url))
    repo = path_parts.pop(0)
    root_dir = path_parts.pop(0) if path_parts else None
    sub_repo = path_parts.pop(0) if path_parts else None
    filename = '/'.join(path_parts)
    return storage_address(hostname, repo, root_dir, sub_repo, filename)
  
check.register_class(storage_address)
