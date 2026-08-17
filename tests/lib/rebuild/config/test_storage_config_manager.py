#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.config.storage_config_manager import storage_config_manager as SCM

class test_storage_config_manager(unit_test):

  def test_basic(self):
    text='''\
[[storage]]
name = "test_local"
provider = "local"
location = "/tmp/loc"
repo = "foo"
root_dir = "bar"

[[storage]]
name = "test_pcloud"
provider = "pcloud"
location = ""
repo = "foo"
root_dir = "bar"
download_username = "fred"
download_password = "flintpass"
upload_username = "fred"
upload_password = "flintpass"

[[storage]]
name = "test_artifactory"
provider = "artifactory"
location = "https://mycorp.jfrog.io/mycorp"
repo = "foo"
root_dir = "bar"
download_username = "fred"
download_password = "flintpass"
upload_username = "admin"
upload_password = "sekret"
'''
    c = SCM(text, '<test>')
    t = c.get('test_local')
    self.assertEqual( 'test_local', t.name )
    self.assertEqual( 'local', t.provider )
    self.assertEqual( '/tmp/loc', t.location )
    self.assertEqual( 'foo', t.repo )
    self.assertEqual( 'bar', t.root_dir )
    self.assertEqual( '', t.download.username )
    self.assertEqual( '', t.download.password )
    self.assertEqual( '', t.upload.username )
    self.assertEqual( '', t.upload.password )

    t = c.get('test_pcloud')
    self.assertEqual( 'test_pcloud', t.name )
    self.assertEqual( 'pcloud', t.provider )
    self.assertEqual( '', t.location )
    self.assertEqual( 'foo', t.repo )
    self.assertEqual( 'bar', t.root_dir )
    self.assertEqual( 'fred', t.download.username )
    self.assertEqual( 'flintpass', t.download.password )
    self.assertEqual( 'fred', t.upload.username )
    self.assertEqual( 'flintpass', t.upload.password )

    t = c.get('test_artifactory')
    self.assertEqual( 'test_artifactory', t.name )
    self.assertEqual( 'artifactory', t.provider )
    self.assertEqual( 'https://mycorp.jfrog.io/mycorp', t.location )
    self.assertEqual( 'foo', t.repo )
    self.assertEqual( 'bar', t.root_dir )
    self.assertEqual( 'fred', t.download.username )
    self.assertEqual( 'flintpass', t.download.password )
    self.assertEqual( 'admin', t.upload.username )
    self.assertEqual( 'sekret', t.upload.password )

  def test_duplicate_name(self):
    text='''\
[[storage]]
name = "test_local"
provider = "local"
location = "/tmp/loc"

[[storage]]
name = "test_local"
provider = "local"
location = "/tmp/loc2"
'''
    with self.assertRaises(SCM.error) as context:
      SCM(text, '<test>')

  def test_make_local_config(self):
    c = SCM.make_local_config('on_the_fly', '/tmp/foo', 'rebuild_stuff', 'root')
    t = c.get('on_the_fly')
    self.assertEqual( 'on_the_fly', t.name )
    self.assertEqual( 'local', t.provider )
    self.assertEqual( '/tmp/foo', t.location )
    self.assertEqual( 'rebuild_stuff', t.repo )
    self.assertEqual( 'root', t.root_dir )

  def test_missing_root_dir(self):
    text='''\
[[storage]]
name = "test_local"
provider = "local"
location = "/tmp/loc"
repo = "foo"
'''
    c = SCM(text, '<test>')
    t = c.get('test_local')
    self.assertEqual( None, t.root_dir )

  def test_empty_root_dir(self):
    text='''\
[[storage]]
name = "test_local"
provider = "local"
location = "/tmp/loc"
repo = "foo"
root_dir = ""
'''
    c = SCM(text, '<test>')
    t = c.get('test_local')
    self.assertEqual( '', t.root_dir )

  def test_missing_repo(self):
    text='''\
[[storage]]
name = "test_local"
provider = "local"
location = "/tmp/loc"
root_dir = "/myroot"
'''
    c = SCM(text, '<test>')
    t = c.get('test_local')
    self.assertEqual( None, t.repo )

  def test_empty_repo(self):
    text='''\
[[storage]]
name = "test_local"
provider = "local"
location = "/tmp/loc"
repo = ""
root_dir = "/myroot"
'''
    c = SCM(text, '<test>')
    t = c.get('test_local')
    self.assertEqual( '', t.repo )

if __name__ == '__main__':
  unit_test.main()
