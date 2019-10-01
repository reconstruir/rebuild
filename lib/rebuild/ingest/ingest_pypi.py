#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import requests
import pprint

from bes.common.check import check
from bes.common.string_util import string_util
from bes.version.software_version import software_version

from .ingest_third_party_info import ingest_third_party_info
from .ingest_third_party_release import ingest_third_party_release

class ingest_pypi(object):

  @classmethod
  def project_info(clazz, name):
    url = 'https://pypi.org/pypi/{}/json'.format(name)
    response = requests.get(url)
    data = response.json()
    info = data['info']
    license = info['license']
    description = info['summary']
    releases = clazz._parse_releases(data['releases'])
    return ingest_third_party_info(name, license, description, releases)
  
  @classmethod
  def _parse_release_entry(clazz, version, entry):
    check.check_dict(entry)
    packagetype = entry['packagetype']
    if packagetype != 'sdist':
      return None
    checksum = entry['digests']['sha256']
    url = entry['url']
    return ingest_third_party_release(version, checksum ,url)
  
  @classmethod
  def _parse_release(clazz, version, entries):
    check.check_list(entries)
    result = [ clazz._parse_release_entry(version, entry) for entry in entries ]
    return [ entry for entry in result if entry ]

  @classmethod
  def _parse_releases(clazz, releases):
    check.check_dict(releases)
    result = []
    for version, entries in releases.items():
      result.extend(clazz._parse_release(version, entries))
    for r in result:
      setattr(r, 'path_hash', clazz._parse_path_hash(r.url))
    return sorted(result, key = lambda entry: software_version.parse_version(entry.version).parts)

  @classmethod
  def _parse_path_hash(clazz, url):
    check.check_string(url)
    a = string_util.remove_head(url, 'https://files.pythonhosted.org/packages/')
    i = a.rfind('/')
    b = a[0:i]
    return b
