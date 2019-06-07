#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.pkg_config.caca_entry import caca_entry
from rebuild.pkg_config.entry_type import entry_type
from bes.text.text_line import text_line

class test_caca_entry(unit_test):

  def test_parse_type(self):
    self.assertEqual( entry_type.VARIABLE, caca_entry.parse(text_line(1, 'prefix=/usr/foo')).etype )
    self.assertEqual( entry_type.PROPERTY, caca_entry.parse(text_line(1, 'Name: foo')).etype )
    self.assertEqual( entry_type.BLANK, caca_entry.parse(text_line(1, '     ')).etype )
    self.assertEqual( entry_type.COMMENT, caca_entry.parse(text_line(1, '# comment foo')).etype )
    self.assertEqual( entry_type.VARIABLE, caca_entry.parse(text_line(1, 'prefix=/usr/foo # with comment')).etype )
    
  def test_parse_variable_value(self):
    self.assertEqual( ( 'prefix', '/usr/foo' ), caca_entry.parse(text_line(1, 'prefix=/usr/foo')).value )
    self.assertEqual( ( 'prefix', '/usr/foo' ), caca_entry.parse(text_line(1, 'prefix = /usr/foo')).value )
    self.assertEqual( ( 'prefix', '/usr/foo' ), caca_entry.parse(text_line(1, 'prefix = /usr/foo ')).value )
    self.assertEqual( ( 'prefix', '/usr/foo' ), caca_entry.parse(text_line(1, ' prefix = /usr/foo ')).value )
    self.assertEqual( ( 'prefix', '/usr/foo' ), caca_entry.parse(text_line(1, 'prefix=/usr/foo # comment')).value )
    
  def test_parse_property_value(self):
    self.assertEqual( ( 'Name', 'foo' ), caca_entry.parse(text_line(1, 'Name=foo')).value )
    self.assertEqual( ( 'Name', 'foo' ), caca_entry.parse(text_line(1, 'Name = foo')).value )
    self.assertEqual( ( 'Name', 'foo' ), caca_entry.parse(text_line(1, 'Name = foo ')).value )
    self.assertEqual( ( 'Name', 'foo' ), caca_entry.parse(text_line(1, ' Name = foo ')).value )
    self.assertEqual( ( 'Name', 'foo' ), caca_entry.parse(text_line(1, 'Name=foo # comment')).value )
    
if __name__ == "__main__":
  unit_test.main()
