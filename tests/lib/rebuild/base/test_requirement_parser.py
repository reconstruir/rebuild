#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base.requirement_parser import requirement_parser as RP

class test_requirement_parser(unit_test):

  def _parse(self, text):
    reqs = [ r for r in RP.parse(text) ]
    return reqs
  
  def test_simplest(self):
    text = 'foo >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None ),
    ], requirements )

  def test_simple(self):
    text = 'apple >= 1.2.3 kiwi pear lychee bananna kiwi-foo orange >= 6.6.6 strawberry >= 1.9'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None ),
      ( 'kiwi', None, None, None ),
      ( 'pear', None, None, None ),
      ( 'lychee', None, None, None ),
      ( 'bananna', None, None, None ),
      ( 'kiwi-foo', None, None, None ),
      ( 'orange', '>=', '6.6.6', None ),
      ( 'strawberry', '>=', '1.9', None ),
    ], requirements )

  def test_white_space(self):
    text = '    apple    >=     1.2.3 kiwi    pear     '
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None ),
      ( 'kiwi', None, None, None ),
      ( 'pear', None, None, None ),
    ], requirements )

  def test_crunched(self):
    text = 'apple'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', None, None, None ),
    ], requirements )

  def test_empty(self):
    text = ''
    requirements = self._parse(text)
    self.assertEqual( [], requirements )

  def test_single(self):
    text = ' apple'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', None, None, None ),
    ], requirements )

  def test_single_versioned(self):
    text = 'apple >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None ),
    ], requirements )

  def test_operators(self):
    text = 'a > 1 b >= 1 c < 1 d <= 1 e == 1 f != 1'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'a', '>', '1', None ),
      ( 'b', '>=', '1', None ),
      ( 'c', '<', '1', None ),
      ( 'd', '<=', '1', None ),
      ( 'e', '==', '1', None ),
      ( 'f', '!=', '1', None ),
    ], requirements )

  def test_multiple(self):
    text = 'foo >= 1.2.3 bar >= 6.6.6'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None ),
      ( 'bar', '>=', '6.6.6', None ),
    ], requirements )

  def test_requirement_with_system(self):
    self.maxDiff = None
    text = 'apple(linux) >= 1.2.3 kiwi orange(macos) == 6.6.6 pear(ios) lychee(all) corn(desktop) tomato(linux|macos) <= 9.8.7'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', 'linux' ),
      ( 'kiwi', None, None, None ),
      ( 'orange', '==', '6.6.6', 'macos' ),
      ( 'pear', None, None, 'ios' ),
      ( 'lychee', None, None, 'all' ),
      ( 'corn', None, None, 'desktop' ),
      ( 'tomato', '<=', '9.8.7', 'linux|macos' ),
    ], requirements )

  def test_global_system_mask(self):
    text = 'all: foo >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'all' ),
    ], requirements )

  def test_global_system_mask_and_override(self):
    text = 'all: foo(linux) >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'linux' ),
    ], requirements )
    
  def test_with_comment(self):
    text = 'all: #foo >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [], requirements )

if __name__ == '__main__':
  unit_test.main()
