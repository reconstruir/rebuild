#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild.pkg_config.entry import entry

class Testentry(unittest.TestCase):

  def test_parse(self):
    self.assertEqual( entry(entry.VARIABLE, 'foo', 'hi'), entry.parse('foo=hi') )
    self.assertEqual( entry(entry.VARIABLE, 'foo', 'prefix=/usr/local'), entry.parse('foo=prefix=/usr/local') )
    self.assertEqual( entry(entry.EXPORT, 'foo', 'prefix=/usr/local'), entry.parse('foo: prefix=/usr/local') )

if __name__ == "__main__":
  unittest.main()
