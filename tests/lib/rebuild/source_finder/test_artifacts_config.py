#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.source_finder import artifacts_config

class test_artifacts_config(unit_test):
    
  def test_basic(self):
    text='''
credential
  provider: pcloud
  type: download
  email: download@bar.com
  password: sekret1

credential
  provider: pcloud
  type: upload
  email: upload@bar.com
  password: sekret2

artifacts
  provider: pcloud
  root_dir: /artifacts

sources
  provider: pcloud
  root_dir: /sources
'''
    ac = artifacts_config(text)
    self.assertEqual( ( 'pcloud', { 'password': 'sekret2', 'root_dir': '/artifacts', 'email': 'upload@bar.com' }, ( '<unknown>', 14 ) ),
                      ac.artifacts_upload )
    self.assertEqual( ( 'pcloud', { 'password': 'sekret1', 'root_dir': '/artifacts', 'email': 'download@bar.com' }, ( '<unknown>', 14 ) ),
                      ac.artifacts_download )
    self.assertEqual( ( 'pcloud', { 'password': 'sekret2', 'root_dir': '/sources', 'email': 'upload@bar.com' }, ( '<unknown>', 18 ) ),
                      ac.sources_upload )
    self.assertEqual( ( 'pcloud', { 'password': 'sekret1', 'root_dir': '/sources', 'email': 'download@bar.com' }, ( '<unknown>', 18 ) ),
                      ac.sources_download )
    
if __name__ == '__main__':
  unit_test.main()
