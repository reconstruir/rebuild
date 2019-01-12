#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file

from rebuild.package.package_file import package_file as FC
from rebuild.package.package_file_list import package_file_list as FCL
  
class test_file_checksum(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/package/package_file'

  A_CHK = '7bf1c5c4153ecb5364b0c7fcb2e767fadc6880e0c2620b69df56b6bb5429448d'
  B_CHK = '429340c7abf63fe50eb3076d3f1d5d996f3b4ee3067734ae8832129af244653c'
  
  def test_from_file(self):
    self.assertEqual( ( 'a.txt', self.A_CHK, False ), FC.from_file('a.txt', False, root_dir = self.data_dir()) )
    self.assertEqual( ( 'b.txt', '429340c7abf63fe50eb3076d3f1d5d996f3b4ee3067734ae8832129af244653c', False ), FC.from_file('b.txt', False, root_dir = self.data_dir()) )
    
  def test_from_files(self):
    self.assertEqual( [
      ( 'a.txt', self.A_CHK, False ),
      ( 'b.txt', self.B_CHK, False ),
    ], FCL.from_files([ 'a.txt', 'b.txt' ], None, root_dir = self.data_dir()) )

  def test_list_from_tuples(self):
    l = FCL([
      ( 'a.txt', self.A_CHK, False ),
      ( 'b.txt', self.B_CHK, False ),
    ])
    self.assertEqual( l, FCL.from_files([ 'a.txt', 'b.txt' ], None, root_dir = self.data_dir()))
    
  def test_to_json(self):
    expected = '''\
[
  [
    "a.txt", 
    "7bf1c5c4153ecb5364b0c7fcb2e767fadc6880e0c2620b69df56b6bb5429448d",
    false
  ], 
  [
    "b.txt", 
    "429340c7abf63fe50eb3076d3f1d5d996f3b4ee3067734ae8832129af244653c",
    false
  ]
]'''
    self.assertEqualIgnoreWhiteSpace( expected, FCL.from_files([ 'a.txt', 'b.txt' ], None, root_dir = self.data_dir()).to_json() )
    
  def test_from_json(self):
    expected = FCL([ FC('a.txt', self.A_CHK, False), FC('b.txt', self.B_CHK, False) ])
    json = '''\
[
  [
    "a.txt", 
    "7bf1c5c4153ecb5364b0c7fcb2e767fadc6880e0c2620b69df56b6bb5429448d", 
    false
  ], 
  [
    "b.txt", 
    "429340c7abf63fe50eb3076d3f1d5d996f3b4ee3067734ae8832129af244653c", 
    false
  ]
]'''
    self.assertEqual( expected, FCL.from_json(json) )
    
  def test_filenames(self):
    a = FCL([ FC('a.txt', self.A_CHK, False), FC('b.txt', self.B_CHK, False) ])
    self.assertEqual( [ 'a.txt', 'b.txt' ], a.filenames() )
    
  def test_verify_true(self):
    a = FCL([ FC('a.txt', self.A_CHK, False), FC('b.txt', self.B_CHK, False) ])
    b = FCL([ FC('a.txt', self.A_CHK, False), FC('b.txt', self.B_CHK, False) ])
    self.assertTrue( a == b )
    
  def test_verify_false(self):
    a = FCL([ FC('a.txt', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', False), FC('b.txt', self.B_CHK, False) ])
    b = FCL([ FC('a.txt', self.A_CHK, False), FC('b.txt', self.B_CHK, False) ])
    self.assertFalse( a == b )
    
  def test_checksum(self):
    a = FCL([ FC('a.txt', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', False), FC('b.txt', self.B_CHK, False) ])
    self.assertEqual( '55b2b2e8f49457879264cf3c357cdefc5a09898ee0d8ba292332a04895303dcb', a.checksum() )
    
if __name__ == '__main__':
  unit_test.main()
    
