#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.url.http_download_cache import http_download_cache
from bes.key_value.key_value_list import key_value_list
from bes.common.string_util import string_util

from .ingest_method_descriptor_base import ingest_method_descriptor_base
from .ingest_method_field import ingest_method_field

class ingest_method_descriptor_http(ingest_method_descriptor_base):
  
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
    )

  #@abstractmethod
  def download(self, args):
    url = string_util.unquote(self._check_download_field(args, 'url'))
    checksum = self._check_download_field(args, 'checksum')
    ingested_filename = self._check_download_field(args, 'ingested_filename')
    cookies_str = self._check_download_field(args, 'cookies', optional = True)
    cookies = key_value_list.parse(cookies_str).to_dict()
    cache_dir = self._check_download_field(args, 'cache_dir')
    cache = http_download_cache(cache_dir)
    return cache.get_url(url, checksum = checksum, cookies = cookies)
