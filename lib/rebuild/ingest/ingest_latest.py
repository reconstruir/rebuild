#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.property.cached_property import cached_property

from .ingest_release import ingest_release

class ingest_latest(namedtuple('ingest_latest', 'name, license, description, releases')):

  def __new__(clazz, name, license, description, releases):
    check.check_string(name)
    check.check_string(license)
    check.check_string(description)
    check.check_ingest_release_seq(releases)
    return clazz.__bases__[0].__new__(clazz, name, license, description, releases)

  @cached_property
  def latest_release(self):
    return self.releases[-1]
  
check.register_class(ingest_latest, include_seq = False)
