#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import json
from bes.common import dict_util
from bes.system import compat
if compat.IS_PYTHON3:
  import urllib.parse as urlparser
  from http.client import RemoteDisconnected as HTTPError
else:
  import urlparse as urlparser
  from urllib2 import HTTPError
  
from bes.testing.unit_test import unit_test
from bes.web import file_web_server, web_server_controller
from bes.archive import archiver, temp_archive
from bes.fs import file_mime, file_util, temp_file
from bes.url import url_util
from bes.fs.testing import temp_content

from rebuild.artifactory.mock_artifactory_server import mock_artifactory_server
from rebuild.artifactory.artifactory_requests import artifactory_requests as AR

from rebuild.storage.storage_address import storage_address

class _test(namedtuple('_test', 'server, root_dir, port')):

  def __new__(clazz, artifactory_id, items = None):
    server = web_server_controller(mock_artifactory_server)
    if items:
      tmp_dir = clazz._make_temp_content(items)
    else:
      tmp_dir = temp_file.make_temp_dir()
    server.start(root_dir = tmp_dir, artifactory_id = artifactory_id)
    port = server.address[1]
    return clazz.__bases__[0].__new__(clazz, server, tmp_dir, port)

  def __str__(self):
    return self.build_path

  @classmethod
  def _make_temp_content(clazz, items):
    tmp_dir = temp_file.make_temp_dir()
    temp_content.write_items(items, tmp_dir)
    return tmp_dir

  def make_url(self, p):
    base = 'http://localhost:%d' % (self.port)
    return urlparser.urljoin(base, p)
  
  def make_address(self, repo, root_dir, sub_repo, filename):
    return storage_address(self.make_url(''), repo, root_dir, sub_repo, filename)
  
  def stop(self):
    self.server.stop()

  def upload(self, address, content):
    tmp_upload = temp_file.make_temp_file(content = content)
    AR.upload(address, tmp_upload, '', '')
    
class test_mock_artifactory_server(unit_test):

  def test_download_url_to_file(self):
    content = [
      'file foo.txt "this is foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "this is baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]

    test = _test('myid', items = content)

    url = test.make_url('foo.txt')

    tmp = temp_file.make_temp_file()
    AR.download_url_to_file(tmp, url, 'myid', 'bar')
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp).mime_type )
    self.assertEqual( 'this is foo.txt\n', file_util.read(tmp, codec = 'utf8') )

    url = test.make_url('subdir/subberdir/baz.txt')
    AR.download_url_to_file(tmp, url, '', '')
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp).mime_type )
    self.assertEqual( 'this is baz.txt\n', file_util.read(tmp, codec = 'utf8') )

    test.stop()

  def test_upload_url(self):
    test = _test('myid')

    tmp = temp_file.make_temp_file(content = 'this is foo.txt\n')
    url = test.make_url('foo.txt')
    AR.upload_url(url, tmp, '', '')
    test.stop()
 
  def test_upload_address(self):
    test = _test('myid')
    tmp_upload = temp_file.make_temp_file(content = 'this is foo.txt\n')
    address = test.make_address('myrepo', 'myrootdir', 'mysubrepo', 'foo.txt')
    AR.upload(address, tmp_upload, '', '')
    tmp_download = temp_file.make_temp_file()
    AR.download_url_to_file(tmp_download, address.url, 'foo', 'bar')
    self.assertEqual( 'this is foo.txt\n', file_util.read(tmp_download) )
    test.stop()
    
  def xtest_list_all_files(self):
    test = _test('myid')

    test.upload(test.make_address('myrepo', 'myrootdir', 'mysubrepo', 'foo.txt'), 'this is foo.txt\n')
    test.upload(test.make_address('myrepo', 'myrootdir', 'mysubrepo', 'bar.txt'), 'this is bar.txt\n')

    result = AR.list_all_files(test.make_address('myrepo', 'myrootdir', 'mysubrepo', None), '', '')
    expected = [
      'sscaca',
    ]
    self.assertEqual( expected, result )
    test.stop()
    
  def test_get_headers_for_url(self):
    test = _test('myid')

    tmp = temp_file.make_temp_file(content = 'this is foo.txt\n')
    url = test.make_url('foo.txt')
    AR.upload_url(url, tmp, '', '')
    headers = AR.get_headers_for_url(url, 'foo', 'bar')
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
    test = _test('myid')

    tmp = temp_file.make_temp_file(content = 'this is foo.txt\n')
    url = test.make_url('foo.txt')
    AR.upload_url(url, tmp, '', '')
    expected = (
      '503900058d0b024b42e2b6d02b45ca5b',
      '33f82b8aa2879fa046b877cfa36158d6607294f9',
      '75f3365f74a5cfbe304b17e1eb4bd99784f609792ffc163cdf4ed464cc08b5ec',
    )
    self.assertEqual( expected, AR.get_checksums_for_url(url, 'foo', 'bar') )
    test.stop()
    
if __name__ == '__main__':
  unit_test.main()
