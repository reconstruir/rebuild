#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from rebuild.pcloud.vfs_pcloud import vfs_pcloud
from bes.credentials.credentials import credentials

#####from unittest import mock
#####
###### This method will be used by the mock to replace requests.get
#####def mocked_requests_get(*args, **kwargs):
#####  print('mocked_requests_get: args={}'.format(args))
#####  print('mocked_requests_get: kwargs={}'.format(kwargs))
#####  
#####  class MockResponse:
#####    def __init__(self, json_data, status_code):
#####      self.json_data = json_data
#####      self.status_code = status_code
#####
#####    def json(self):
#####      return self.json_data
#####
#####  if args[0] == 'http://someurl.com/test.json':
#####    return MockResponse({"key1": "value1"}, 200)
#####  elif args[0] == 'http://someotherurl.com/anothertest.json':
#####    return MockResponse({"key2": "value2"}, 200)
#####
#####  return MockResponse(None, 404)

class test_vfs_pcloud(unit_test):

#  @mock.patch('requests.get', side_effect = mocked_requests_get)
  def test_something(self):
    return
    cred = credentials('<unittest>', email = 'user@example.com', password = 'sekret')
    tmp_cache_dir = self.make_temp_dir()
    fs = vfs_pcloud('<unittest>', cred, cache_dir = tmp_cache_dir)
    info = fs.file_info('/mydir/myfile.txt')
    
if __name__ == "__main__":
  unit_test.main()
