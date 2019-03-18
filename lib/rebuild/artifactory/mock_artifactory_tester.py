#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
#import os
#from os import path
#from bes.archive import archiver
from bes.fs import file_util, temp_file
#from bes.git.git_unit_test import git_unit_test
from bes.web import file_web_server, web_server_controller
#from bes.git import repo as git_repo, temp_git_repo
#from bes.url import url_util
#
from rebuild.artifactory.mock_artifactory_server import mock_artifactory_server
from rebuild.storage.storage_address import storage_address
#
#from bes.testing.unit_test import unit_test
#
#from ego_automation.artifactory.artifactory import artifactory
#
from bes.system import compat

if compat.IS_PYTHON3:
  import urllib.parse as urlparse
else:
  import urlparse as urlparse

class mock_artifactory_tester(namedtuple('mock_artifactory_tester', 'server, root_dir, port')):

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
    return urlparse.urljoin(base, p)
  
  def make_address(self, repo, root_dir, sub_repo, filename):
    return storage_address(self.make_url(''), repo, root_dir, sub_repo, filename)
  
  def stop(self):
    self.server.stop()

#  def upload(self, address, content):
#    tmp_upload = temp_file.make_temp_file(content = content)
#    AR.upload(address, tmp_upload, '', '')
