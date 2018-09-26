#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common import json_util
import json, os.path as path

from rebuild.source_finder import source_finder_db_file as F
from rebuild.source_finder import source_finder_db_entry as E

class test_source_finder_db_file(unit_test):

  TEST_JSON = '''{
  "a/foo.tgz": [
    "a/foo.tgz", 
    66.6, 
    "c1"
  ], 
  "b/bar.tgz": [
    "b/bar.tgz", 
    66.7, 
    "c2"
  ], 
  "c/baz.tgz": [
    "c/baz.tgz", 
    66.8, 
    "c3"
  ]
}'''
  
  def test_from_json(self):
    self.assertEqual( {
      'a/foo.tgz': E('a/foo.tgz', 66.6, 'c1'),
      'b/bar.tgz': E('b/bar.tgz', 66.7, 'c2'),
      'c/baz.tgz': E('c/baz.tgz', 66.8, 'c3'),
      }, F.from_json(self.TEST_JSON) )
    
  def test_from_json_object(self):
    self.assertEqual( {
      'a/foo.tgz': E('a/foo.tgz', 66.6, 'c1'),
      'b/bar.tgz': E('b/bar.tgz', 66.7, 'c2'),
      'c/baz.tgz': E('c/baz.tgz', 66.8, 'c3'),
      }, F.from_json_object(json.loads(self.TEST_JSON)) )
    
  def test_to_json(self):
    f = F()
    f['a/foo.tgz'] = E('a/foo.tgz', 66.6, 'c1')
    f['b/bar.tgz'] = E('b/bar.tgz', 66.7, 'c2')
    f['c/baz.tgz'] = E('c/baz.tgz', 66.8, 'c3')
    self.assertMultiLineEqual( self.TEST_JSON, f.to_json() )
    
if __name__ == '__main__':
  unit_test.main()
