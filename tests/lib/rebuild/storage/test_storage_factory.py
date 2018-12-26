#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.fs import temp_file

from rebuild.config import storage_config
from rebuild.storage import storage_factory
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
  def remote_filename_abs(self, remote_filename):
    assert False

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
  def remote_filename_abs(self, remote_filename):
    assert False

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
credential
  provider: kiwi
  purpose: download
  username: download@bar.com
  password: downloadpss

credential
  provider: kiwi
  purpose: upload
  username: upload@bar.com
  password: uploadpass

storage
  description: where i upload to kiwi
  provider: kiwi
  root_dir: /mydir
'''
    ac = storage_config(config_text, '<test>')

    provider = 'kiwi'
    a = ac.get('download', provider)
    self.assertEqual( 'download@bar.com', a.credentials.username )
    self.assertEqual( 'downloadpss', a.credentials.password )
    self.assertEqual( '/mydir', a.root_dir )

    b = ac.get('upload', provider)
    self.assertEqual( 'upload@bar.com', b.credentials.username )
    self.assertEqual( 'uploadpass', b.credentials.password )
    self.assertEqual( '/mydir', b.root_dir )

    download_credentials = ac.get('download', provider)
    upload_credentials = ac.get('upload', provider)
    local_storage_dir = temp_file.make_temp_dir()
    factory_config = storage_factory.config(local_storage_dir, 'myrepo', False, download_credentials, upload_credentials)
    kiwi_storage = storage_factory.create(provider, factory_config)

if __name__ == '__main__':
  unit_test.main()
