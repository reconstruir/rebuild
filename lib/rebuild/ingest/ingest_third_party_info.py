#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.property.cached_property import cached_property

from .ingest_third_party_release import ingest_third_party_release

class ingest_third_party_info(namedtuple('ingest_third_party_info', 'name, license, description, releases')):

  def __new__(clazz, name, license, description, releases):
    check.check_string(name)
    check.check_string(license)
    check.check_string(description)
    check.check_ingest_third_party_release_seq(releases)
    return clazz.__bases__[0].__new__(clazz, name, license, description, releases)

  @cached_property
  def latest_release(self):
    return self.releases[-1]

  def find_by_version(self, version):
    l = filter(lambda entry: entry.version == version, self.releases)
    if len(l) != 1:
      raise ValueError('Multiple releases with version "{}" found'.format(version))
    return l[0]
  
check.register_class(ingest_third_party_info, include_seq = False)
