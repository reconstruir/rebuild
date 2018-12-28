#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.config import new_storage_config as SC

class test_new_storage_config(unit_test):
    
  def xtest_artifactory(self):
    text='''
storage
  description: artifactory something
  provider: artifactory
  location: https://myname.jfrog.io/myname
  repo: repo-name
  root_dir: rebuild_stuff
  download.username: ${ARTIFACTORY_DOWNLOAD_USERNAME}
  download.password: ${ARTIFACTORY_DOWNLOAD_PASSWORD}
  upload.username: ${ARTIFACTORY_UPLOAD_USERNAME}
  upload.password: ${ARTIFACTORY_UPLOAD_PASSWORD}
'''
    ac = SC(text, '<test>')

    a = ac.get('download', 'pcloud')
    self.assertEqual( 'download@bar.com', a.credentials.username )
    self.assertEqual( 'downloadpss', a.credentials.password )
    self.assertEqual( '/mydir', a.root_dir )

    b = ac.get('upload', 'pcloud')
    self.assertEqual( 'upload@bar.com', b.credentials.username )
    self.assertEqual( 'uploadpass', b.credentials.password )
    self.assertEqual( '/mydir', b.root_dir )
    
  def xtest_combined_upload_download(self):
    text='''
credential
  provider: pcloud
  purpose: download upload
  username: foo@bar.com
  password: sekret

storage
  description: mine personal pcloud account
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

  def xtest_missing_upload(self):
    text='''
credential
  provider: pcloud
  purpose: download
  username: download@bar.com
  password: sekret1

storage
  description: mine personal pcloud account
  provider: pcloud
  root_dir: /mydir
'''
    with self.assertRaises(storage_config.error) as context:
      storage_config(text, '<test>')

  def xtest_make_local_config(self):
    ac = storage_config.make_local_config('on the fly config', '/tmp/foo', 'rebuild_stuff')

    a = ac.get('download', 'local')
    self.assertEqual( None, a.credentials.username )
    self.assertEqual( None, a.credentials.password )
    self.assertEqual( 'rebuild_stuff', a.root_dir )

    b = ac.get('upload', 'local')
    self.assertEqual( None, b.credentials.username )
    self.assertEqual( None, b.credentials.password )
    self.assertEqual( 'rebuild_stuff', b.root_dir )
      
  def xtest_many_providers(self):
    text = '''
credential
  provider: artifactory
  purpose: download
  username: downuser
  password: downpass

credential
  provider: artifactory
  purpose: upload
  username: upuser
  password: uppass

credential
  provider: pcloud
  purpose: download upload
  username: foo@bar.com
  password: ppass

storage
  provider: artifactory
  hostname: https://example.com:8081
  root_dir: /artdir

storage
  provider: pcloud
  root_dir: /pmydir

storage
  provider: git
  address: git@example.com:myproj/myrepo.git
  root_dir: /gmydir
  no_credentials: true

storage
  provider: local
  root_dir: /tmp/tmpdir
  no_credentials: true
'''

    ac = storage_config(text, '<test>')

    a = ac.get('download', 'artifactory')
    self.assertEqual( 'downuser', a.credentials.username )
    self.assertEqual( 'downpass', a.credentials.password )
    self.assertEqual( '/artdir', a.root_dir )

    a = ac.get('upload', 'artifactory')
    self.assertEqual( 'upuser', a.credentials.username )
    self.assertEqual( 'uppass', a.credentials.password )
    self.assertEqual( '/artdir', a.root_dir )
    
    a = ac.get('download', 'pcloud')
    self.assertEqual( 'foo@bar.com', a.credentials.username )
    self.assertEqual( 'ppass', a.credentials.password )
    self.assertEqual( '/pmydir', a.root_dir )

    a = ac.get('upload', 'pcloud')
    self.assertEqual( 'foo@bar.com', a.credentials.username )
    self.assertEqual( 'ppass', a.credentials.password )
    self.assertEqual( '/pmydir', a.root_dir )
    
    a = ac.get('download', 'git')
    self.assertEqual( None, a.credentials.username )
    self.assertEqual( None, a.credentials.password )
    self.assertEqual( '/gmydir', a.root_dir )
    self.assertEqual( { 'address': 'git@example.com:myproj/myrepo.git' }, a.values )
    a = ac.get('upload', 'git')
    self.assertEqual( None, a.credentials.username )
    self.assertEqual( None, a.credentials.password )
    self.assertEqual( '/gmydir', a.root_dir )
    self.assertEqual( { 'address': 'git@example.com:myproj/myrepo.git' }, a.values )

    a = ac.get('download', 'local')
    self.assertEqual( None, a.credentials.username )
    self.assertEqual( None, a.credentials.password )
    self.assertEqual( '/tmp/tmpdir', a.root_dir )
    a = ac.get('upload', 'local')
    self.assertEqual( None, a.credentials.username )
    self.assertEqual( None, a.credentials.password )
    self.assertEqual( '/tmp/tmpdir', a.root_dir )
    
if __name__ == '__main__':
  unit_test.main()
