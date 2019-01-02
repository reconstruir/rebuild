#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.common import dict_util
from bes.testing.unit_test import unit_test
from bes.testing.unit_test.unit_test_skip import skip_if
from bes.fs import file_util, temp_file
from rebuild.artifactory.artifactory_requests import artifactory_requests as AR

class test_artifactory_requests(unit_test):

  _download_username = os.environ.get('_BES_ARTIFACTORY_DOWNLOAD_USERNAME', None)
  _download_password = os.environ.get('_BES_ARTIFACTORY_DOWNLOAD_PASSWORD', None)
  _upload_username = os.environ.get('_BES_ARTIFACTORY_UPLOAD_USERNAME', None)
  _upload_password = os.environ.get('_BES_ARTIFACTORY_UPLOAD_PASSWORD', None)
  _have_credentials = _download_username is not None and _download_password is not None and _upload_username is not None and _upload_password is not None
  if not unit_test.BES_DONET:
    _reason = 'BES_DONET not set.'
  elif not _have_credentials:
    _reason = 'credentials not set.'
  else:
    _reason = ''
  _enabled = unit_test.BES_DONET and _have_credentials

  @skip_if(not _enabled, _reason)
  def test_fetch_heders(self):
    url = 'https://withme.jfrog.io/withme/ego-dev-env-tools/dev-env/sources/r/rsa-3.4.2.tar.gz'
    headers = AR.fetch_headers(url, self._download_username, self._download_password)
    self.assertEqual( {
      'X-Checksum-Md5': 'b315f47882c24030ee6b5aad628cccdb',
      'X-Checksum-Sha1': '5e01533d344df8e55c090f0fce9c5f9383bf9e9c',
      'X-Checksum-Sha256': '25df4e10c263fb88b5ace923dd84bf9aa7f5019687b5e55382ffcdb8bede9db5',
      'X-Artifactory-Filename': 'rsa-3.4.2.tar.gz',
      'X-Artifactory-Id': 'aolshared4b-withme',
                       }, dict_util.filter_with_keys(headers, [ 'X-Checksum-Sha1', 'X-Checksum-Md5', 'X-Artifactory-Filename', 'X-Artifactory-Id', 'X-Checksum-Sha256' ]) )

  @skip_if(not _enabled, _reason)
  def test_fetch_checksums(self):
    url = 'https://withme.jfrog.io/withme/ego-dev-env-tools/dev-env/sources/r/rsa-3.4.2.tar.gz'
    checksums = AR.fetch_checksums(url, self._download_username, self._download_password)
    self.assertEqual( ( 'b315f47882c24030ee6b5aad628cccdb', '5e01533d344df8e55c090f0fce9c5f9383bf9e9c', '25df4e10c263fb88b5ace923dd84bf9aa7f5019687b5e55382ffcdb8bede9db5' ), checksums )

  @skip_if(not _enabled, _reason)
  def test_download_to_file(self):
    url = 'https://withme.jfrog.io/withme/ego-dev-env-tools/dev-env/sources/r/rsa-3.4.2.tar.gz'
    tmp = temp_file.make_temp_file()
    rv = AR.download_to_file(tmp, url, self._download_username, self._download_password)
    self.assertTrue( '25df4e10c263fb88b5ace923dd84bf9aa7f5019687b5e55382ffcdb8bede9db5', file_util.checksum('sha256', tmp) )

if __name__ == '__main__':
  unit_test.main()
