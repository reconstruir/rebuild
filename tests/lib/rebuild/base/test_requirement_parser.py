#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base.requirement_parser import requirement_parser as RP
from rebuild.base.requirement import requirement_hardness

class test_requirement_parser(unit_test):

  def _parse(self, text):
    reqs = [ r for r in RP.parse(text) ]
    return reqs
  
  def test_simplest(self):
    text = 'foo >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None, None, None ),
    ], requirements )

  def test_simple(self):
    text = 'apple >= 1.2.3 kiwi pear lychee bananna kiwi-foo orange >= 6.6.6 strawberry >= 1.9'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None, None, None ),
      ( 'kiwi', None, None, None, None, None ),
      ( 'pear', None, None, None, None, None ),
      ( 'lychee', None, None, None, None, None ),
      ( 'bananna', None, None, None, None, None ),
      ( 'kiwi-foo', None, None, None, None, None ),
      ( 'orange', '>=', '6.6.6', None, None, None ),
      ( 'strawberry', '>=', '1.9', None, None, None ),
    ], requirements )

  def test_white_space(self):
    text = '    apple    >=     1.2.3 kiwi    pear     '
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None, None, None ),
      ( 'kiwi', None, None, None, None, None ),
      ( 'pear', None, None, None, None, None ),
    ], requirements )

  def test_crunched(self):
    text = 'apple'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', None, None, None, None, None ),
    ], requirements )

  def test_empty(self):
    text = ''
    requirements = self._parse(text)
    self.assertEqual( [], requirements )

  def test_single(self):
    text = ' apple'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', None, None, None, None, None ),
    ], requirements )

  def test_single_versioned(self):
    text = 'apple >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None, None, None ),
    ], requirements )

  def test_operators(self):
    text = 'a > 1 b >= 1 c < 1 d <= 1 e == 1 f != 1'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'a', '>', '1', None, None, None ),
      ( 'b', '>=', '1', None, None, None ),
      ( 'c', '<', '1', None, None, None ),
      ( 'd', '<=', '1', None, None, None ),
      ( 'e', '==', '1', None, None, None ),
      ( 'f', '!=', '1', None, None, None ),
    ], requirements )

  def test_multiple(self):
    text = 'foo >= 1.2.3 bar >= 6.6.6'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None, None, None ),
      ( 'bar', '>=', '6.6.6', None, None, None ),
    ], requirements )

  def test_requirement_with_system(self):
    self.maxDiff = None
    text = 'apple(linux) >= 1.2.3 kiwi orange(macos) == 6.6.6 pear(ios) lychee(all) corn(desktop) tomato(linux|macos) <= 9.8.7'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', 'linux', None, None ),
      ( 'kiwi', None, None, None, None, None ),
      ( 'orange', '==', '6.6.6', 'macos', None, None ),
      ( 'pear', None, None, 'ios', None, None ),
      ( 'lychee', None, None, 'all', None, None ),
      ( 'corn', None, None, 'desktop', None, None ),
      ( 'tomato', '<=', '9.8.7', 'linux|macos', None, None ),
    ], requirements )

  def test_global_system_mask(self):
    text = 'all: foo >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'all', None, None ),
    ], requirements )

  def test_global_system_mask_and_override(self):
    text = 'all: foo(linux) >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'linux', None, None ),
    ], requirements )
    
  def test_with_comment(self):
    text = 'all: #foo >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [], requirements )

  def test_hardness(self):
    r = self._parse('all: RUN foo >= 1.2.3')
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'all', 'RUN', None ),
    ], r )

  def test_hardness_multiple(self):
    r = self._parse('all: RUN foo >= 1.2.3 BUILD bar >= 6.6.6')
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'all', 'RUN', None ),
      ( 'bar', '>=', '6.6.6', 'all', 'BUILD', None ),
    ], r )
    self.assertTrue( isinstance(r[0][4], requirement_hardness) )
    self.assertTrue( isinstance(r[1][4], requirement_hardness) )

  def test_expression(self):
    text = 'all(${KIWI_VERSION} < 666): foo >= 1.2.3'
    requirements = self._parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'all', None, '${KIWI_VERSION} < 666' ),
    ], requirements )
    
if __name__ == '__main__':
  unit_test.main()
