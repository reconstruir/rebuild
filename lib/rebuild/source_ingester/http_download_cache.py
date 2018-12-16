#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import shutil
import os.path as path
from bes.system import log
from bes.common import check, string_util
from bes.fs import file_util, temp_file
from bes.git import git_util

class http_download_cache(object):
  'A git download cache.'

  def __init__(self, root_dir):
    self.root_dir = root_dir
    
  def has_url(self, url):
    'Return True if the tarball with address and revision is in the cache.'
    local_cached_path = self._path_for_url(address)
    return path.exists(local_cached_path)

  def get_url(self, url, checksum, cookies = None, debug = False):
    'Return the local filesystem path to the tarball with address and revision.'
    self.log_d('get_url: url=%s; checksum=%s; cookies=%s' % (url, checksum, cookies))
    local_cached_path = self._path_for_url(url)
    self.log_d('get_url: local_cached_path=%s' % (local_cached_path))
    if path.exists(local_cached_path):
      if file_util.checksum('sha256', local_cached_path) == checksum:
        self.log_d('get_url: found in cache with good checksum. using: %s' % (local_cached_path))
        return local_cached_path
      else:
        self.log_d('get_url: found in cache with BAD checksum. removing: %s' % (local_cached_path))
        file_util.remove(local_cached_path)
    tmp = self._download_to_tmp_file(url, cookies = cookies, debug = debug)
    self.log_d('get_url: downloaded url to %s' % (tmp))
    if not tmp:
      self.log_d('get_url: failed to download: %s' % (url))
      return None
    if file_util.checksum('sha256', tmp) == checksum:
      self.log_d('get_url: download succesful and checksum is good.  using: %s' % (local_cached_path))
      file_util.rename(tmp, local_cached_path)
    self.log_d('get_url: download worked but checksum was BAD: %s' % (local_cached_path))
    return None
    
  def _path_for_url(self, url):
    'Return path for local tarball.'
    return path.join(self.root_dir, git_util.sanitize_address(url))

#  def tarball_path(self, address, revision):
#    'Return True if the tarball with address and revision is in the cache.'
#    local_cached_path = self._path_for_url(address)
#    tarball_filename = '%s.tar.gz' % (revision)
#    return path.join(local_cached_path, tarball_filename)

  @classmethod
  def _download_to_tmp_file(clazz, url, cookies, debug = False):
    'Download url to tmp file.'
    import requests
    tmp = temp_file.make_temp_file(delete = not debug)
    clazz.log_d('_download_to_tmp_file: url=%s; tmp=%s' % (url, tmp))
    response = requests.get(url, stream = True, cookies = cookies or None)
    clazz.log_d('_download_to_tmp_file: status_code=%d' % (response.status_code))
    if response.status_code != 200:
      return None
    with open(tmp, 'wb') as fout:
      shutil.copyfileobj(response.raw, fout)
      fout.close()
      return tmp
  
check.register_class(http_download_cache, include_seq = False)
log.add_logging(http_download_cache, 'http_download_cache')
