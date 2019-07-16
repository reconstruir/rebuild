#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .ingest_method_descriptor_base import ingest_method_descriptor_base
from .ingest_method_field import ingest_method_field

class ingest_method_descriptor_download(ingest_method_descriptor_base):
  
  #@abstractmethod
  def method(self):
    return 'download'

  #@abstractmethod
  def fields(self):
    return (
      ingest_method_field('url'),
      ingest_method_field('checksum'),
      ingest_method_field('ingested_filename'),
      ingest_method_field('cookies', optional = True),
    )
