#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe.value import value_parsing as P

class test_value_parsing(unit_test):

  def test_split_mask_and_value(self):
    self.assertEqual( ( 'all', 'foo' ), P.split_mask_and_value('all: foo') )
    self.assertEqual( ( 'all', 'foo' ), P.split_mask_and_value('all:foo') )
    self.assertEqual( ( 'all', 'foo' ), P.split_mask_and_value(' all:foo') )
    self.assertEqual( ( 'all', 'foo' ), P.split_mask_and_value(' all:foo ') )
    self.assertEqual( ( 'all', 'foo' ), P.split_mask_and_value(' all: foo ') )
    self.assertEqual( ( 'all', 'foo' ), P.split_mask_and_value(' all :foo ') )
    self.assertEqual( ( 'all', 'foo' ), P.split_mask_and_value(' all : foo ') )
    self.assertEqual( ( 'all', 'foo' ), P.split_mask_and_value('all : foo') )

  def test_strip_mask(self):
    self.assertEqual( 'foo', P.strip_mask('all: foo') )
    self.assertEqual( 'foo', P.strip_mask('all:foo') )
    self.assertEqual( 'foo', P.strip_mask(' all:foo') )
    self.assertEqual( 'foo', P.strip_mask(' all:foo ') )
    self.assertEqual( 'foo', P.strip_mask(' all: foo ') )
    self.assertEqual( 'foo', P.strip_mask(' all :foo ') )
    self.assertEqual( 'foo', P.strip_mask(' all : foo ') )
    self.assertEqual( 'foo', P.strip_mask('all : foo') )

if __name__ == '__main__':
  unit_test.main()
