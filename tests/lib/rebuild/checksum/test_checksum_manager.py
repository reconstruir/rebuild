#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.checksum.checksum_manager import checksum_manager
from bes.fs.temp_file import temp_file

class test_checksum_manager(unit_test):

  def test_ignore_all(self):
    m = self._make_temp_checksum_manager()
    self.assertFalse( m.ignore_all )
    m.ignore_all = True
    self.assertTrue( m.ignore_all )
    
  def test_ignore(self):
    m = self._make_temp_checksum_manager()
    self.assertFalse( m.is_ignored('foo') )
    m.ignore('foo')
    self.assertTrue( m.is_ignored('foo') )
    
  @classmethod
  def _make_temp_checksum_manager(self):
    tmp_checksum_dir = temp_file.make_temp_dir()
    m = checksum_manager(tmp_checksum_dir)
    return m

if __name__ == '__main__':
  unit_test.main()
