#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.storage.file_mapping import file_mapping as SFM
import os.path as path

class test_file_mapping(unit_test):
  
  def test_remote_to_local(self):
    m = SFM('/home/foo', '/remote/foo', 'http://example.com')
    self.assertEqual( '/home/foo/a', m.remote_to_local('/remote/foo/a') )
    self.assertEqual( '/home/foo/a', m.remote_to_local('remote/foo/a') )
    self.assertEqual( '/home/foo', m.remote_to_local('/remote/foo') )
    
  def test_local_to_remote(self):
    m = SFM('/home/foo', '/remote/foo', 'http://example.com')
    self.assertEqual( '/remote/foo/a', m.local_to_remote('/home/foo/a') )
    self.assertEqual( '/remote/foo/a', m.local_to_remote('home/foo/a') )
    self.assertEqual( '/remote/foo', m.local_to_remote('/home/foo') )
    
  def test_remote_path(self):
    m = SFM('/local', '/remote', None)
    self.assertEqual( '/remote/a', m.remote_path('/a') )
    self.assertEqual( '/remote/a', m.remote_path('a') )
    self.assertEqual( '/remote', m.remote_path('/') )
    self.assertEqual( '/remote', m.remote_path('') )
    self.assertEqual( '/remote/a/b', m.remote_path('/a/b') )

    m = SFM('/local', '/remote/', None)
    self.assertEqual( '/remote/a', m.remote_path('/a') )
    self.assertEqual( '/remote/a', m.remote_path('a') )
    self.assertEqual( '/remote', m.remote_path('/') )
    self.assertEqual( '/remote', m.remote_path('') )
    self.assertEqual( '/remote/a/b', m.remote_path('/a/b') )

    m = SFM('/local', 'remote', None)
    self.assertEqual( '/remote/a', m.remote_path('/a') )
    self.assertEqual( '/remote/a', m.remote_path('a') )
    self.assertEqual( '/remote', m.remote_path('/') )
    self.assertEqual( '/remote', m.remote_path('') )
    self.assertEqual( '/remote/a/b', m.remote_path('/a/b') )
    
  def test_local_path(self):
    m = SFM('/local', '/local', None)
    self.assertEqual( '/local/a', m.local_path('/a') )
    self.assertEqual( '/local/a', m.local_path('a') )
    self.assertEqual( '/local', m.local_path('/') )
    self.assertEqual( '/local', m.local_path('') )
    self.assertEqual( '/local/a/b', m.local_path('/a/b') )

    m = SFM('/local', '/local/', None)
    self.assertEqual( '/local/a', m.local_path('/a') )
    self.assertEqual( '/local/a', m.local_path('a') )
    self.assertEqual( '/local', m.local_path('/') )
    self.assertEqual( '/local', m.local_path('') )
    self.assertEqual( '/local/a/b', m.local_path('/a/b') )

    m = SFM('/local', 'local', None)
    self.assertEqual( '/local/a', m.local_path('/a') )
    self.assertEqual( '/local/a', m.local_path('a') )
    self.assertEqual( '/local', m.local_path('/') )
    self.assertEqual( '/local', m.local_path('') )
    self.assertEqual( '/local/a/b', m.local_path('/a/b') )

  def test_url(self):
    self.assertEqual( 'http://example.com/', SFM('/local', '/remote', 'http://example.com/').url )
    self.assertEqual( 'http://example.com/', SFM('/local', '/remote', 'http://example.com').url )
    
  def test_make_url(self):
    m = SFM('/l', '/r', 'http://x.com/')
    self.assertEqual( 'http://x.com/a', m.make_url('a') )
    self.assertEqual( 'http://x.com/a', m.make_url('a/') )
    self.assertEqual( 'http://x.com/a', m.make_url('/a') )
    self.assertEqual( 'http://x.com/a/b', m.make_url('a/b') )
    self.assertEqual( 'http://x.com/', m.make_url('/') )
    self.assertEqual( 'http://x.com/', m.make_url('') )
    
if __name__ == '__main__':
  unit_test.main()
