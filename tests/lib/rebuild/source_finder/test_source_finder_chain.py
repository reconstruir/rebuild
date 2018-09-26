#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.source_finder import source_finder_chain, source_finder_hard_coded

from test_source_finder_local import source_dir_maker

class test_source_finder_chain(unit_test):

  def test_find_empty(self):
    chain = source_finder_chain()
    self.assertEqual( None, chain.find_source('alpha', '1.2.3', 'linux') )
    
  def test_find_one_finder(self):
    tarball = source_dir_maker.make_tarball('tar.gz')
    chain = source_finder_chain()
    chain.add_finder(source_finder_hard_coded(tarball, 'alpha', '1.2.3'))
    self.assertEqual( tarball, chain.find_source('alpha', '1.2.3', 'linux') )
    
  def xtest_find_two_finders(self):
    chain = source_finder_chain()

    tarball1 = source_dir_maker.make_tarball('tar.gz')
    chain.add_finder(source_finder_hard_coded(tarball1, 'alpha', '1.2.3'))

    tarball2 = source_dir_maker.make_tarball('zip')
    chain.add_finder(source_finder_hard_coded(tarball2, 'beta', '6.6.6'))

    self.assertEqual( tarball1, chain.find_source('alpha', '1.2.3', 'linux') )
    self.assertEqual( tarball2, chain.find_source('beta', '6.6.6', 'linux') )
    
if __name__ == '__main__':
  unit_test.main()
