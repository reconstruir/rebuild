#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.storage.storage_address import storage_address as SA

class test_storage_address(unit_test):

  def test_hostname(self):
    self.assertEqual( 'http://mycom.not/mycom/', SA('http://mycom.not/mycom', 'r', 'd', None, 'f').hostname )
    self.assertEqual( 'http://mycom.not/mycom/', SA('http://mycom.not/mycom/', 'r', 'd', None, 'f').hostname )

  def test_repo(self):
    self.assertEqual( 'repo', SA('http://mycom.not/mycom', 'repo', 'd', None, 'f').repo )
    self.assertEqual( 'repo', SA('http://mycom.not/mycom', 'repo/', 'd', None, 'f').repo )
    self.assertEqual( 'repo', SA('http://mycom.not/mycom', '/repo', 'd', None, 'f').repo )
    self.assertEqual( 'repo', SA('http://mycom.not/mycom', '/repo/', 'd', None, 'f').repo )

  def test_sub_repo(self):
    self.assertEqual( None, SA('http://mycom.not/mycom', 'r', 'd', None, 'f').sub_repo )
    self.assertEqual( 'sub', SA('http://mycom.not/mycom', 'r', 'd', 'sub', 'f').sub_repo )
    self.assertEqual( 'sub', SA('http://mycom.not/mycom', 'r', 'd', 'sub/', 'f').sub_repo )
    self.assertEqual( 'sub', SA('http://mycom.not/mycom', 'r', 'd', '/sub', 'f').sub_repo )
    self.assertEqual( 'sub', SA('http://mycom.not/mycom', 'r', 'd', '/sub/', 'f').sub_repo )
    
  def test_filename(self):
    self.assertEqual( None, SA('http://mycom.not/mycom', 'r', 'd', 's', None).filename )
    self.assertEqual( 'f', SA('http://mycom.not/mycom', 'r', 'd', 's', 'f').filename )
    self.assertEqual( 'f', SA('http://mycom.not/mycom', 'r', 'd', 's', '/f').filename )
    
  def test_url(self):
    self.assertEqual( 'http://mycom.not/mycom/repo/root/subrepo/foo/bar/something-1.1.2.tar.gz',
                      SA('http://mycom.not/mycom', 'repo', 'root', 'subrepo', 'foo/bar/something-1.1.2.tar.gz').url )
    self.assertEqual( 'http://mycom.not/mycom/repo/root/foo/bar/something-1.1.2.tar.gz',
                      SA('http://mycom.not/mycom', 'repo', 'root', None, 'foo/bar/something-1.1.2.tar.gz').url )
    self.assertEqual( 'http://mycom.not/mycom/repo/root/subrepo',
                      SA('http://mycom.not/mycom', 'repo', 'root', 'subrepo', None).url )
    
  def test_mutate_filename(self):
    self.assertEqual( 'newf', SA('http://mycom.not/mycom', 'r', 'd', 's', None).mutate_filename('newf').filename )
    self.assertEqual( 'newf', SA('http://mycom.not/mycom', 'r', 'd', 's', 'f').mutate_filename('newf').filename )
    self.assertEqual( 'newf', SA('http://mycom.not/mycom', 'r', 'd', 's', '/f').mutate_filename('newf').filename )
    
    
if __name__ == '__main__':
  unit_test.main()
