#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.archive.archive_extension import archive_extension
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
    return self.find_by_version(self.releases[-1].version)

  def find_by_version(self, version):
    found = filter(lambda entry: entry.version == version, self.releases)
    if not found:
      raise ValueError('No version found for "{}": {}"'.format(self.name, version))
    return self._find_with_tar(found)
  
  def _find_with_tar(self, releases):
    'Return the first release that is tar.  We prefer tar over zip if available.'
    for release in releases:
      if archive_extension.is_valid_tar_ext(release.url):
        return release
    return releases[0]
  
check.register_class(ingest_third_party_info, include_seq = False)
