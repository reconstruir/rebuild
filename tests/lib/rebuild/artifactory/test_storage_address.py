#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.artifactory.storage_address import storage_address as AA

class test_storage_address(unit_test):

  def test_hostname(self):
    self.assertEqual( 'http://mycom.not/mycom/', AA('http://mycom.not/mycom', 'r', 'd', None, 'f').hostname )
    self.assertEqual( 'http://mycom.not/mycom/', AA('http://mycom.not/mycom/', 'r', 'd', None, 'f').hostname )

  def test_repo(self):
    self.assertEqual( 'repo', AA('http://mycom.not/mycom', 'repo', 'd', None, 'f').repo )
    self.assertEqual( 'repo', AA('http://mycom.not/mycom', 'repo/', 'd', None, 'f').repo )
    self.assertEqual( 'repo', AA('http://mycom.not/mycom', '/repo', 'd', None, 'f').repo )
    self.assertEqual( 'repo', AA('http://mycom.not/mycom', '/repo/', 'd', None, 'f').repo )

  def test_sub_repo(self):
    self.assertEqual( None, AA('http://mycom.not/mycom', 'r', 'd', None, 'f').sub_repo )
    self.assertEqual( 'sub', AA('http://mycom.not/mycom', 'r', 'd', 'sub', 'f').sub_repo )
    self.assertEqual( 'sub', AA('http://mycom.not/mycom', 'r', 'd', 'sub/', 'f').sub_repo )
    self.assertEqual( 'sub', AA('http://mycom.not/mycom', 'r', 'd', '/sub', 'f').sub_repo )
    self.assertEqual( 'sub', AA('http://mycom.not/mycom', 'r', 'd', '/sub/', 'f').sub_repo )
    
  def test_filename(self):
    self.assertEqual( None, AA('http://mycom.not/mycom', 'r', 'd', 's', None).filename )
    self.assertEqual( 'f', AA('http://mycom.not/mycom', 'r', 'd', 's', 'f').filename )
    self.assertEqual( 'f', AA('http://mycom.not/mycom', 'r', 'd', 's', '/f').filename )
    
  def test_url(self):
    self.assertEqual( 'http://mycom.not/mycom/repo/root/subrepo/foo/bar/something-1.1.2.tar.gz',
                      AA('http://mycom.not/mycom', 'repo', 'root', 'subrepo', 'foo/bar/something-1.1.2.tar.gz').url )
    self.assertEqual( 'http://mycom.not/mycom/repo/root/foo/bar/something-1.1.2.tar.gz',
                      AA('http://mycom.not/mycom', 'repo', 'root', None, 'foo/bar/something-1.1.2.tar.gz').url )
    self.assertEqual( 'http://mycom.not/mycom/repo/root/subrepo',
                      AA('http://mycom.not/mycom', 'repo', 'root', 'subrepo', None).url )
    
  def test_api_url(self):
    self.assertEqual( 'http://mycom.not/mycom/api',
                      AA('http://mycom.not/mycom', 'repo', 'root', None, None).api_url )
    
  def test_search_aql_url(self):
    self.assertEqual( 'http://mycom.not/mycom/api/search/aql',
                      AA('http://mycom.not/mycom', 'repo', 'root', None, None).search_aql_url )
    
if __name__ == '__main__':
  unit_test.main()
