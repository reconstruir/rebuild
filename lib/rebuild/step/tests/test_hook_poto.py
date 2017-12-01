#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.step import hook_poto

class test_hook_poto(unit_test):

  __unit_test_data_dir__ = 'test_data/hook'

  def test_parse(self):
    self.assertEqual( hook_poto('foo.py', 'func'), hook_poto.parse('foo.py:func') )

  def test_parse_list(self):
    self.assertEqual( [ hook_poto('foo.py', 'func1'), hook_poto('bar.py', 'func2') ], hook_poto.parse_list( [ 'foo.py:func1', 'bar.py:func2' ]) )

  def test_set_root_dir(self):
    h = hook_poto('foo.py', 'func')
    self.assertEqual( 'foo.py', h.filename )
    h.root_dir = '/tmp/'
    self.assertEqual( '/tmp/foo.py', h.filename )
    self.assertEqual( 'func', h.function_name )

  def test_execute(self):
    h = hook_poto('myhookfile.py', 'my_hook_func')
    h.root_dir = self.data_dir()
    self.assertEqual( 'myhookprivate:script:env:args', h.execute('script', 'env', 'args') )
    
if __name__ == '__main__':
  unit_test.main()
