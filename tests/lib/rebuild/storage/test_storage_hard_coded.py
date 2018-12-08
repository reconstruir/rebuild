#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.storage import storage_hard_coded

from test_storage_local import source_dir_maker

class test_storage_hard_coded(unit_test):

  def test_find_tarball(self):
    tarball = source_dir_maker.make_tarball('tar.gz')
    finder = storage_hard_coded(tarball)
    self.assertEqual( tarball,
                      finder.find_tarball('alpha-1.2.3.tar.gz') )

if __name__ == '__main__':
  unit_test.main()
