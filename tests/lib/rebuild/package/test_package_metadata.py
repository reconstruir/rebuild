#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
import os.path as path
#from bes.fs import temp_file, temp_item
from rebuild.package import package_metadata as PM

class test_package_metadata(unit_test):

  def test_to_json(self):
    pass
    #a = PM('foo', '1.0.0', 'macos', [ 'x86_64' ], 'lib', 'release', [], [], [], 

if __name__ == '__main__':
  unit_test.main()
