#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.source_finder import hard_coded_source_finder

from test_local_source_finder import source_dir_maker

class test_hard_coded_source_finder(unit_test):

  def test_find_source(self):
    tarball = source_dir_maker.make_tarball('tar.gz')
    name = 'alpha'
    version = '1.2.3'
    finder = hard_coded_source_finder(tarball, name, version)
    self.assertEqual( tarball,
                      finder.find_source(name, version, 'linux') )

  def test_find_source_not_found(self):
    tarball = source_dir_maker.make_tarball('tar.gz')
    name = 'alpha'
    version = '1.2.3'
    finder = hard_coded_source_finder(tarball, name, version)
    self.assertEqual( None, finder.find_source('other', '25', 'linux') )
    
if __name__ == '__main__':
  unit_test.main()
