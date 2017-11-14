#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
#import os.path as path
#from bes.fs import temp_file
#from rebuild.base import build_category, build_target, package_descriptor, requirement
from rebuild.packager import package_resolver

class test_package_resolver(unit_test):

  def test_caca(self):
    pass

if __name__ == '__main__':
  unit_test.main()
