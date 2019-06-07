#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.script_unit_test import script_unit_test
from bes.system.host import host

class test_rebuild_ar(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/binary_objects'
  __script__ = __file__, '../../bin/rebuild_ar_replacement.py'

  def test_contents(self):
    rv = self.run_script([ 't', self.platform_data_path('libarm64.a') ])
    if host.SYSTEM == host.MACOS:
      expected = '''
__.SYMDEF SORTED
cherry.o
kiwi.o
'''
    else:
      expected = '''
cherry.o
kiwi.o
'''
      
      
    self.assertEqual( 0, rv.exit_code )
    self.assert_string_equal_strip( expected, rv.output )

if __name__ == '__main__':
  script_unit_test.main()
