#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from rebuild.storage import storage_db_entry
import os.path as path

class test_storage_db_dict(unit_test):

  def test_from_list(self):
    self.assertEqual( ( 'x/y/foo.tgz', 666.666, 'chk' ), storage_db_entry.from_list([ 'x/y/foo.tgz', 666.666, 'chk' ]) )

  def test_to_list(self):
    self.assertEqual( [ 'x/y/foo.tgz', 666.666, 'chk' ], storage_db_entry( 'x/y/foo.tgz', 666.666, 'chk' ).to_list() )
  
if __name__ == '__main__':
  unit_test.main()
