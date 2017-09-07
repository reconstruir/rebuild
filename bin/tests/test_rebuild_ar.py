#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.unit_test import script_unit_test

class test_rebuild_ar(script_unit_test):

  __unit_test_data_dir__ = '../../rebuild/test_data/binary_objects'
  __script__ = __file__, '../rebuild_ar.py'

  def test_contents(self):
    rv = self.run_command('t', self.platform_data_path('libarm64.a'))
    expected = '''
__.SYMDEF SORTED
cherry.o
kiwi.o
'''
    self.assertEqual( 0, rv.exit_code )
    self.assert_string_equal_strip( expected, rv.stdout )

if __name__ == '__main__':
  script_unit_test.main()
