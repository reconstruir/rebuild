#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.source_finder import artifacts_config
from bes.config.simple_config import error as config_error

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
    ac = artifacts_config(text, '<test>')
    self.assertEqual( ( 'pcloud', { 'password': 'sekret2', 'root_dir': '/artifacts', 'email': 'upload@bar.com' }, ( '<test>', 14 ) ),
                      ac.artifacts_upload )
    self.assertEqual( ( 'pcloud', { 'password': 'sekret1', 'root_dir': '/artifacts', 'email': 'download@bar.com' }, ( '<test>', 14 ) ),
                      ac.artifacts_download )
    self.assertEqual( ( 'pcloud', { 'password': 'sekret2', 'root_dir': '/sources', 'email': 'upload@bar.com' }, ( '<test>', 18 ) ),
                      ac.sources_upload )
    self.assertEqual( ( 'pcloud', { 'password': 'sekret1', 'root_dir': '/sources', 'email': 'download@bar.com' }, ( '<test>', 18 ) ),
                      ac.sources_download )

  def test_env_var(self):
    text='''
credential
  provider: pcloud
  type: download
  email: download@bar.com
  password: ${SEKRET1}

credential
  provider: pcloud
  type: upload
  email: upload@bar.com
  password: ${SEKRET2}

artifacts
  provider: pcloud
  root_dir: /artifacts

sources
  provider: pcloud
  root_dir: /sources
'''

    os.environ['SEKRET1'] = 'sekret1'
    os.environ['SEKRET2'] = 'sekret2'
    ac = artifacts_config(text, '<test>')
    del os.environ['SEKRET1']
    del os.environ['SEKRET2']
    self.assertEqual( ( 'pcloud', { 'password': 'sekret2', 'root_dir': '/artifacts', 'email': 'upload@bar.com' }, ( '<test>', 14 ) ),
                      ac.artifacts_upload )
    self.assertEqual( ( 'pcloud', { 'password': 'sekret1', 'root_dir': '/artifacts', 'email': 'download@bar.com' }, ( '<test>', 14 ) ),
                      ac.artifacts_download )
    self.assertEqual( ( 'pcloud', { 'password': 'sekret2', 'root_dir': '/sources', 'email': 'upload@bar.com' }, ( '<test>', 18 ) ),
                      ac.sources_upload )
    self.assertEqual( ( 'pcloud', { 'password': 'sekret1', 'root_dir': '/sources', 'email': 'download@bar.com' }, ( '<test>', 18 ) ),
                      ac.sources_download )
    
  def test_env_var_missing(self):
    text='''
credential
  provider: pcloud
  type: download
  email: download@bar.com
  password: ${SEKRET1}

credential
  provider: pcloud
  type: upload
  email: upload@bar.com
  password: ${SEKRET2}

artifacts
  provider: pcloud
  root_dir: /artifacts

sources
  provider: pcloud
  root_dir: /sources
'''

    with self.assertRaises(config_error) as context:
      artifacts_config(text, '<test>')
    
if __name__ == '__main__':
  unit_test.main()
