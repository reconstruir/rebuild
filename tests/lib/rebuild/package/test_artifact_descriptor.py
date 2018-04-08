#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.package import artifact_descriptor as AD

class test_artifact_descriptor(unit_test):

  def xtest_parse_filename(self):
    f = AD.parse_artifact_filename
    self.assertEqual( ( 'foo', ), f('macos/x86_64/release/gnu_libtool-2.4.6.tar.gz') )
    
if __name__ == '__main__':
  unit_test.main()
