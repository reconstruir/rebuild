#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.testing import temp_content

class test_local_finder(unit_test):

  def test_local_finder(self):
    tmp_dir = temp_content.write_items_temp_dir([
      'file a/alpha-1.2.3.tar.gz "alpha-1.2.3.tar.gz" 644',
      'file b/beta-1.2.3.tar.gz "beta-1.2.3.tar.gz" 644',
    ])
  
if __name__ == '__main__':
  unit_test.main()
