#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from bes.common.dict_util import dict_util
from bes.common.tuple_util import tuple_util
from bes.system.compat import compat

if compat.IS_PYTHON3:
  import urllib.parse as urlparse
  from http.client import RemoteDisconnected as HTTPError
else:
  import urlparse as urlparse
  from urllib2 import HTTPError
  
from bes.testing.unit_test import unit_test
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list

from rebuild.artifactory.mock_artifactory_tester import mock_artifactory_tester as MAT
from rebuild.artifactory.artifactory_requests import artifactory_requests as AR
from rebuild.credentials.credentials import credentials

class test_mock_artifactory_server(unit_test):

  _TEST_CRED = credentials(username = '', password = '')
  
  def test_download_url_to_file(self):
    content = [
      'file foo.txt "this is foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "this is baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]

    test = MAT('myid', items = content)

    url = test.make_url('foo.txt')

    tmp = temp_file.make_temp_file()
    AR.download_url_to_file(tmp, url, self._TEST_CRED)
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp).mime_type )
    self.assertEqual( 'this is foo.txt\n', file_util.read(tmp, codec = 'utf8') )

    url = test.make_url('subdir/subberdir/baz.txt')
    AR.download_url_to_file(tmp, url, self._TEST_CRED)
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp).mime_type )
    self.assertEqual( 'this is baz.txt\n', file_util.read(tmp, codec = 'utf8') )

    test.stop()

  def test_upload_url(self):
    test = MAT('myid')

    tmp = temp_file.make_temp_file(content = 'this is foo.txt\n')
    url = test.make_url('foo.txt')
    AR.upload_url(url, tmp, self._TEST_CRED)
    test.stop()
 
  def test_upload_address(self):
    test = MAT('myid')
    tmp_upload = temp_file.make_temp_file(content = 'this is foo.txt\n')
    address = test.make_address('myrepo', 'myrootdir', 'mysubrepo', 'foo.txt')
    AR.upload(address, tmp_upload, self._TEST_CRED)
    tmp_download = temp_file.make_temp_file()
    AR.download_url_to_file(tmp_download, address.url, self._TEST_CRED)
    self.assertEqual( 'this is foo.txt\n', file_util.read(tmp_download, codec = 'utf-8') )
    test.stop()
    
  def xtest_list_files(self):
    test = MAT('myid')

    test.upload(test.make_address('myrepo', 'myrootdir', 'mysubrepo', 'foo.txt'), 'this is foo.txt\n')
    test.upload(test.make_address('myrepo', 'myrootdir', 'mysubrepo', 'bar.txt'), 'this is bar.txt\n')

    result = AR.list_files(test.make_address('myrepo', 'myrootdir', 'mysubrepo', None), self._TEST_CRED)
    expected = [
      'sscaca',
    ]
    self.assertEqual( expected, result )
    test.stop()
    
  def test_get_headers_for_url(self):
    test = MAT('myid')

    tmp = temp_file.make_temp_file(content = 'this is foo.txt\n')
    url = test.make_url('foo.txt')
    AR.upload_url(url, tmp, self._TEST_CRED)
    headers = AR.get_headers_for_url(url, self._TEST_CRED)
    headers = dict_util.filter_with_keys(headers, [ 'X-Checksum-Sha1', 'X-Checksum-Md5', 'X-Artifactory-Filename', 'X-Artifactory-Id', 'X-Checksum-Sha256' ])
    
    self.assertEqual( {
      'X-Checksum-Md5': '503900058d0b024b42e2b6d02b45ca5b',
      'X-Checksum-Sha1': '33f82b8aa2879fa046b877cfa36158d6607294f9',
      'X-Checksum-Sha256': '75f3365f74a5cfbe304b17e1eb4bd99784f609792ffc163cdf4ed464cc08b5ec',
      'X-Artifactory-Filename': 'foo.txt',
      'X-Artifactory-Id': 'myid',
    }, headers )
    test.stop()
    
  def test_get_checksums_for_url(self):
    test = MAT('myid')

    tmp = temp_file.make_temp_file(content = 'this is foo.txt\n')
    url = test.make_url('foo.txt')
    AR.upload_url(url, tmp, self._TEST_CRED)
    expected = (
      '503900058d0b024b42e2b6d02b45ca5b',
      '33f82b8aa2879fa046b877cfa36158d6607294f9',
      '75f3365f74a5cfbe304b17e1eb4bd99784f609792ffc163cdf4ed464cc08b5ec',
    )
    self.assertEqual( expected, AR.get_checksums_for_url(url, self._TEST_CRED) )
    test.stop()
    
  def test_get_checksums_for_url(self):
    test = MAT('myid')

    tmp = temp_file.make_temp_file(content = 'this is foo.txt\n')
    url = test.make_url('foo.txt')
    AR.upload_url(url, tmp, self._TEST_CRED)
    expected = AR._file_info(
      'foo.txt',
      '16',
      'text/plain; charset=us-ascii',
      'xThu, 04 Apr 2019 01:54:21 GMT',
      None,
      None,
      '503900058d0b024b42e2b6d02b45ca5b',
      '33f82b8aa2879fa046b877cfa36158d6607294f9',
      '75f3365f74a5cfbe304b17e1eb4bd99784f609792ffc163cdf4ed464cc08b5ec',
    )
    actual = AR.get_file_info_url(url, self._TEST_CRED)

    self.assertMultiLineEqual( self._file_info_to_string(expected), self._file_info_to_string(actual) )
    test.stop()

  @classmethod
  def _file_info_to_string(clazz, fi):
    fi = tuple_util.clone(fi, mutations = { 'date': '${DATE}' })
    return '\n'.join([ '{}={}'.format(x[0], x[1]) for x in fi._asdict().items() ])
    
if __name__ == '__main__':
  unit_test.main()
