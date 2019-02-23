#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from bes.system import compat
if compat.IS_PYTHON3:
  import urllib.request as urlopener
  import urllib.parse as urlparser
  from http.client import RemoteDisconnected as HTTPError
else:
  import urllib2 as urlopener
  import urlparse as urlparser
  from urllib2 import HTTPError
  
from bes.testing.unit_test import unit_test
from bes.web import file_web_server, web_server_controller
from bes.archive import archiver, temp_archive
from bes.fs import file_mime, file_util, temp_file
from bes.url import url_util
from bes.fs.testing import temp_content

from rebuild.artifactory.mock_artifactory_server import mock_artifactory_server

class test_mock_artifactory_server(unit_test):

  DEBUG = unit_test.DEBUG

  @classmethod
  def _make_temp_content(clazz, items):
    tmp_dir = temp_file.make_temp_dir()
    temp_content.write_items(items, tmp_dir)
    return tmp_dir
  
  def test_tarball_server(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "this is foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "this is baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])

    server = web_server_controller(mock_artifactory_server)
    server.start(root_dir = tmp_dir)
    port = server.address[1]

    url = self._make_url(port, 'foo.txt')
    tmp = url_util.download_to_temp_file(url)
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp).mime_type )
    self.assertEqual( 'this is foo.txt\n', file_util.read(tmp, codec = 'utf8') )

    url = self._make_url(port, 'subdir/subberdir/baz.txt')
    tmp = url_util.download_to_temp_file(url)
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp).mime_type )
    self.assertEqual( 'this is baz.txt\n', file_util.read(tmp, codec = 'utf8') )

    with self.assertRaises(HTTPError) as ctx:
      url = self._make_url(port, 'notthere.txt')
      tmp = url_util.download_to_temp_file(url)

    server.stop()

  @classmethod
  def _make_url(clazz, port, p):
    base = 'http://localhost:%d' % (port)
    return urlparser.urljoin(base, p)
  
if __name__ == '__main__':
  unit_test.main()
