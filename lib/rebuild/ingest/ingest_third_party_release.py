#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check

class ingest_third_party_release(namedtuple('ingest_third_party_release', 'version, checksum, url')):

  def __new__(clazz, version, checksum, url):
    check.check_string(version)
    check.check_string(checksum)
    check.check_string(url)
    return clazz.__bases__[0].__new__(clazz, version, checksum, url)

check.register_class(ingest_third_party_release)
  
