#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.archive.archive_extension import archive_extension
from bes.archive.archiver import archiver
from bes.common.string_util import string_util
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.key_value.key_value_list import key_value_list
from bes.system.log import logger
from bes.url.http_download_cache import http_download_cache

from .ingest_method_descriptor_base import ingest_method_descriptor_base
from .ingest_method_field import ingest_method_field
from .ingest_error import ingest_error

class ingest_method_descriptor_http(ingest_method_descriptor_base):

  log = logger('ingest')
  
  #@abstractmethod
  def method(self):
    return 'http'

  #@abstractmethod
  def fields(self):
    return (
      ingest_method_field('url'),
      ingest_method_field('checksum'),
      ingest_method_field('ingested_filename'),
      ingest_method_field('cookies', optional = True),
      ingest_method_field('arcname', optional = True),
    )

  #@abstractmethod
  def download(self, args):
    url = string_util.unquote(self._check_download_field(args, 'url'))
    checksum = self._check_download_field(args, 'checksum')
    ingested_filename = self._check_download_field(args, 'ingested_filename')
    arcname = self._check_download_field(args, 'arcname', optional = True)
    cookies_str = self._check_download_field(args, 'cookies', optional = True)
    cookies = key_value_list.parse(cookies_str).to_dict()
    cache_dir = self._check_download_field(args, 'cache_dir')
    cache = http_download_cache(cache_dir)
    try:
      local_download = cache.get_url(url, checksum = checksum, cookies = cookies)
    except Exception as ex:
      msg = 'Failed to download "{}" - {}'.format(url, str(ex))
      raise ingest_error(msg)
      
    self.log.log_d('ingest_method_descriptor_http: local_download={}'.format(local_download))
    self.log.log_d('ingest_method_descriptor_http: arcname={}'.format(arcname))
    if arcname:
      ext = archive_extension.extension_for_filename(ingested_filename)
      tmp_dir = temp_file.make_temp_dir()
      tmp_filename = path.join(tmp_dir, arcname)
      file_util.copy(local_download, tmp_filename)
      os.chmod(tmp_filename, 0o0755)
      tmp_archive = archiver.create_temp_file(ext, tmp_dir)
      return tmp_archive
    return local_download
