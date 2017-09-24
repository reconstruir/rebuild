#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild import hook

class test_hook(unit_test):

  __unit_test_data_dir__ = 'test_data/hook'

  def test_parse(self):
    self.assertEqual( hook('foo.py', 'func'), hook.parse('foo.py:func') )

  def test_parse_list(self):
    self.assertEqual( [ hook('foo.py', 'func1'), hook('bar.py', 'func2') ], hook.parse_list( [ 'foo.py:func1', 'bar.py:func2' ]) )

  def test_set_root_dir(self):
    h = hook('foo.py', 'func')
    self.assertEqual( 'foo.py', h.filename )
    h.root_dir = '/tmp/'
    self.assertEqual( '/tmp/foo.py', h.filename )
    self.assertEqual( 'func', h.function_name )

  def test_execute(self):
    h = hook('myhookfile.py', 'my_hook_func')
    h.root_dir = self.data_dir()
    self.assertEqual( 'foo:bar', h.execute('bar') )
    
if __name__ == '__main__':
  unit_test.main()
