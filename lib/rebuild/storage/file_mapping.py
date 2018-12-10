#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system import execute, log, os_env
from bes.common import check
from bes.fs import file_util
from bes.compat.url_compat import urlparse, urljoin

from collections import namedtuple

class file_mapping(namedtuple('file_mapping', 'local_root, remote_root, url')):
  'A class to manage file mappings between a remote server and local disk.'

  def __new__(clazz, local_root, remote_root, url):
    check.check_string(local_root)
    local_root = clazz._normalize_abs_path(local_root)
    check.check_string(remote_root)
    remote_root = clazz._normalize_abs_path(remote_root)
    if url:
      check.check_string(url)
      url = clazz._check_url(url)
    return clazz.__bases__[0].__new__(clazz, local_root, remote_root, url)
  
  @classmethod
  def _normalize_abs_path(clazz, p):
    return file_util.ensure_lsep(file_util.rstrip_sep(p))
      
  @classmethod
  def _normalize_rel_path(clazz, p):
    return file_util.strip_sep(p)
      
  def remote_path(self, relative_path):
    relative_path = self._normalize_rel_path(relative_path)
    if not relative_path:
      return self.remote_root
    return path.join(self.remote_root, self._normalize_rel_path(relative_path))

  def local_path(self, relative_path):
    relative_path = self._normalize_rel_path(relative_path)
    if not relative_path:
      return self.local_root
    return path.join(self.local_root, self._normalize_rel_path(relative_path))
  
  def remote_to_local(self, remote_path):
    remote_path = self._normalize_abs_path(remote_path)
    if remote_path == self.remote_root:
      return self.local_root
    remote_base = self._remote_base(remote_path)
    return path.join(self.local_root, remote_base)
    
  def local_to_remote(self, local_path):
    local_path = self._normalize_abs_path(local_path)
    if local_path == self.local_root:
      return self.remote_root
    local_base = self._local_base(local_path)
    return path.join(self.remote_root, local_base)

  def make_url(self, relative_path):
    relative_path = self._normalize_rel_path(relative_path)
    return urljoin(self.url, relative_path)
  
  def url_for_remote(self, remote_path):
    if not self._host_url:
      return None
    remote_path_with_base = path.join(self._host_path, file_util.lstrip_sep(remote_path))
    return urljoin(self._host_url, remote_path_with_base)
    
  def url_for_local(self, local_path):
    if not self._host_url:
      return None
    remote_path = self.local_to_remote(local_path)
    return self.url_for_remote(remote_path)
  
  def _remote_base(self, remote_path):
    'Return the base of a remote path relative to the remote root.'
    return file_util.remove_head(remote_path, self.remote_root)

  def _local_base(self, local_path):
    'Return the base of a local path relative to the local root.'
    return file_util.remove_head(local_path, self.local_root)

  @classmethod
  def _check_url(clazz, url):
    rv = urlparse(url)
    if rv.query:
      raise ValueError('url should not have a query: %s' % (url))
    if rv.params:
      raise ValueError('url should not have a params: %s' % (url))
    if rv.fragment:
      raise ValueError('url should not have a fragment: %s' % (url))
    if rv.path and rv.path != '/':
      raise ValueError('url should not have a path: %s' % (url))
    if not url.endswith('/'):
      url = url + '/'
    return url
  
