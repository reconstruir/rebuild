#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common import json_util, string_util
import json, os.path as path

from rebuild.source_finder import source_finder_db_dict as F
from rebuild.source_finder import source_finder_db_entry as E

class test_source_finder_db_dict(unit_test):

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
    self.assert_json_equal( self.TEST_JSON, f.to_json() )
    
  def test_files(self):
    f = F.from_json(self.TEST_JSON)
    self.assertEqual( [ 'a/foo.tgz', 'b/bar.tgz', 'c/baz.tgz' ], F.from_json(self.TEST_JSON).files() )

  def test_mtime(self):
    f = F.from_json(self.TEST_JSON)
    self.assertEqual( 66.6, f.mtime('a/foo.tgz') )
    
  def test_checksum(self):
    f = F.from_json(self.TEST_JSON)
    self.assertEqual( 'c1', f.checksum('a/foo.tgz') )
    
  def test_contains(self):
    f = F.from_json(self.TEST_JSON)
    self.assertEqual( True, 'a/foo.tgz' in f )
    self.assertEqual( False, 'notthere.tgz' in f )
    
  def test_delta(self):
    fa = self._parse_db('apple/foo.tgz 66.6 c1, s/strawberry.tgz 66.7 c2, k/kiwi.tgz 66.8 c3')
    fb = self._parse_db('apple/foo.tgz 66.6 c1, s/strawberry.tgz 66.7 c2, k/kiwi.tgz 66.8 c3')
    d = fa.delta(fb)
    print('DELTA: %s' % (str(d)))

  @classmethod
  def _parse_item(clazz, s):
    parts = string_util.split_by_white_space(s, strip = True)
    assert len(parts) == 3
    name = parts[0]
    mtime = float(parts[1])
    checksum = parts[2]
    return E(name, mtime, checksum)

  @classmethod
  def _parse_db(clazz, s):
    db = {}
    for x in s.split(','):
      x = x.strip()
      if x:
        item = clazz._parse_item(x)
        assert not item.filename in db
        db[item.filename] = item
    return F(db = db)
  
  @classmethod
  def _db_item_to_string(clazz, item):
    return '%s %s %s' % (item.filename, item.mtime, item.checksum)
  
  @classmethod
  def _db_to_string(clazz, db):
    return ', '.join([ clazz._db_item_to_string(item) for item in db.items() ])
  
if __name__ == '__main__':
  unit_test.main()
