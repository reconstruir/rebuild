#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.fs.temp_file import temp_file

from rebuild.config.storage_config_manager import storage_config_manager
from rebuild.storage.storage_factory import storage_factory
from rebuild.storage.storage_base import storage_base

class storage_kiwi(storage_base):

  def __init__(self, config):
    self.where = path.join(config.local_cache_dir, 'kiwi')
    
  def __str__(self):
    return 'kiwi:%s' % (self.where)

  #@abstractmethod
  def reload_available(self):
    pass
  
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

  #@abstractmethod
  def upload(self, local_filename, remote_filename):
    pass

  #@abstractmethod
  def set_properties(self, filename, properties):
    assert False
  
  #@abstractmethod
  def remote_checksum(self, remote_filename):
    pass

  #@abstractmethod
  def list_all_files(self):
    assert False
    
class storage_watermelon(storage_base):

  def __init__(self, config):
    self.where = path.join(config.local_cache_dir, 'watermelon')
    
  def __str__(self):
    return 'watermelon:%s' % (self.where)

  #@abstractmethod
  def reload_available(self):
    pass
  
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

  #@abstractmethod
  def upload(self, local_filename, remote_filename):
    pass

  #@abstractmethod
  def set_properties(self, filename, properties):
    assert False
  
  #@abstractmethod
  def remote_checksum(self, remote_filename):
    pass

  #@abstractmethod
  def list_all_files(self):
    assert False
    
class test_storage_factory(unit_test):

  def test_has_provider(self):
    self.assertTrue( storage_factory.has_provider('kiwi') )
    self.assertTrue( storage_factory.has_provider('watermelon') )
    self.assertFalse( storage_factory.has_provider('orange') )
  
  def test_create(self):
    config_text = '''
storage
  name: test
  provider: kiwi
  location: kiwi://mykiwi.com/mystuff
  repo: myrepo
  root_dir: myrootdir
  download.username: fred
  download.password: flintpass
  upload.username: admin
  upload.password: sekret
'''
    scm = storage_config_manager(config_text, '<test>')
    config = scm.get('test')
    self.assertEqual( 'test', config.name )
    self.assertEqual( 'kiwi', config.provider )
    self.assertEqual( 'kiwi://mykiwi.com/mystuff', config.location )
    self.assertEqual( 'myrepo', config.repo )
    self.assertEqual( 'myrootdir', config.root_dir )
    self.assertEqual( 'fred', config.download.username )
    self.assertEqual( 'flintpass', config.download.password )
    self.assertEqual( 'admin', config.upload.username )
    self.assertEqual( 'sekret', config.upload.password )

    local_storage_dir = temp_file.make_temp_dir()
    factory_config = storage_factory.config(local_storage_dir, 'mysubrepo', False, config)
    storage = storage_factory.create(factory_config)
    self.assertTrue( isinstance(storage, storage_kiwi) )

if __name__ == '__main__':
  unit_test.main()
