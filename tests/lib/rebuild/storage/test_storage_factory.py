#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from rebuild.config import storage_config
from rebuild.storage import storage_factory
from rebuild.storage.storage_base import storage_base

class storage_kiwi(storage_base):

  def __init__(self, config):
    self.where = path.join(config.local_cache_dir, 'kiwi')
    
  def __str__(self):
    return 'kiwi:%s' % (self.where)
    
  #@abstractmethod
  def find_tarball(self, filename):
    return self._find_by_filename(self.where, filename)

  #@abstractmethod
  def ensure_source(self, filename):
    assert path.isabs(filename)
    return path.isfile(filename)
  
  #@abstractmethod
  def search(self, name):
    pass
  
class storage_watermelon(storage_base):

  def __init__(self, config):
    self.where = path.join(config.local_cache_dir, 'watermelon')
    
  def __str__(self):
    return 'watermelon:%s' % (self.where)
    
  #@abstractmethod
  def find_tarball(self, filename):
    return self._find_by_filename(self.where, filename)

  #@abstractmethod
  def ensure_source(self, filename):
    assert path.isabs(filename)
    return path.isfile(filename)
  
  #@abstractmethod
  def search(self, name):
    pass
  
class test_storage_factory(unit_test):

  def test_has_provider(self):
    self.assertTrue( SF.has_provider('kiwi') )
    self.assertTrue( SF.has_provider('watermelon') )
    self.assertFalse( SF.has_provider('orange') )
  
  def test_create(self):
    config_text = '''
credential
  provider: kiwi
  purpose: download
  email: kiwi_download@bar.com
  password: kiwipassdown

credential
  provider: kiwi
  purpose: upload
  email: kiwi_upload@bar.com
  password: kiwipassup

storage
  name: mine_kiwi
  description: mine personal kiwi account
#  purpose: artifacts sources
  provider: kiwi
  root_dir: /kiwi_root
'''
    ac = storage_config(config_text, '<test>')
    a = ac.find('artifacts', 'mine_kiwi')
    self.assertEqual( {
      'email': 'download@bar.com',
      'password': 'sekret1',
      'root_dir': '/mydir',
    }, a.credentials.download )
    self.assertEqual( {
      'email': 'upload@bar.com',
      'password': 'sekret2',
      'root_dir': '/mydir',
    }, a.credentials.upload )


    
    kiwi = SF.create('kiwi', config):    self.assertTrue( SF.has_provider('kiwi') )
    self.assertFalse( SF.has_provider('orange') )
  
if __name__ == '__main__':
  unit_test.main()
