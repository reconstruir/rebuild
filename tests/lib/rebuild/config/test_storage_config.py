#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.config import storage_config

class test_storage_config(unit_test):
    
  def test_basic(self):
    text='''
credential
  provider: pcloud
  purpose: download
  username: download@bar.com
  password: downloadpss

credential
  provider: pcloud
  purpose: upload
  username: upload@bar.com
  password: uploadpass

storage
  description: where i upload to pcloud
  provider: pcloud
  purpose: upload
  root_dir: /mydir/uploads

storage
  description: where i download from pcloud
  provider: pcloud
  purpose: download
  root_dir: /mydir/downloads
'''
    ac = storage_config(text, '<test>')

    a = ac.get('download', 'pcloud')
    self.assertEqual( 'download@bar.com', a.credentials.username )
    self.assertEqual( 'downloadpss', a.credentials.password )
    self.assertEqual( '/mydir/downloads', a.root_dir )

    b = ac.get('upload', 'pcloud')
    self.assertEqual( 'upload@bar.com', b.credentials.username )
    self.assertEqual( 'uploadpass', b.credentials.password )
    self.assertEqual( '/mydir/uploads', b.root_dir )
    
  def test_combined_upload_download(self):
    text='''
credential
  provider: pcloud
  purpose: download upload
  username: foo@bar.com
  password: sekret

storage
  description: mine personal pcloud account
  purpose: upload download
  provider: pcloud
  root_dir: /mydir
'''
    ac = storage_config(text, '<test>')

    a = ac.get('download', 'pcloud')
    self.assertEqual( 'foo@bar.com', a.credentials.username )
    self.assertEqual( 'sekret', a.credentials.password )
    self.assertEqual( '/mydir', a.root_dir )

    b = ac.get('upload', 'pcloud')
    self.assertEqual( 'foo@bar.com', b.credentials.username )
    self.assertEqual( 'sekret', b.credentials.password )
    self.assertEqual( '/mydir', b.root_dir )

  def test_missing_upload(self):
    text='''
credential
  provider: pcloud
  purpose: download
  username: download@bar.com
  password: sekret1

storage
  description: mine personal pcloud account
  purpose: upload download
  provider: pcloud
  root_dir: /mydir
'''
    with self.assertRaises(storage_config.error) as context:
      storage_config(text, '<test>')

  def test_make_local_config(self):
    ac = storage_config.make_local_config('on the fly config', '/tmp/foo')

    a = ac.get('download', 'local')
    self.assertEqual( None, a.credentials.username )
    self.assertEqual( None, a.credentials.password )
    self.assertEqual( '/tmp/foo', a.root_dir )

    b = ac.get('upload', 'local')
    self.assertEqual( None, b.credentials.username )
    self.assertEqual( None, b.credentials.password )
    self.assertEqual( '/tmp/foo', b.root_dir )
      
if __name__ == '__main__':
  unit_test.main()
