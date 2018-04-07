#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
import os, os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from rebuild.package.env_dir import env_dir, action

class test_env_dir(unit_test):

  def test_foo(self):
    os.environ['SOMETHINGIMADEUP'] = 'GOOD'

    save_path = os.environ['PATH']
    test_path = '/bin:/usr/bin:/my/path:/sbin'
    os.environ['PATH'] = test_path

    try:
      tmp_dir = temp_file.make_temp_dir()
      file_util.save(path.join(tmp_dir, '1.sh'), content = 'export PATH=/bin:/usr/bin:/sbin\n')
      file_util.save(path.join(tmp_dir, '2.sh'), content = 'export BAR=orange\n')
      file_util.save(path.join(tmp_dir, '3.sh'), content = 'export PATH=/a/bin:$PATH\nexport PATH=/b/bin:$PATH\n')
      file_util.save(path.join(tmp_dir, '4.sh'), content = 'export FOO=kiwi\n')
      file_util.save(path.join(tmp_dir, '5.sh'), content = 'export PATH=$PATH:/x/bin\nPATH=$PATH:/y/bin\n')
      file_util.save(path.join(tmp_dir, '6.sh'), content = 'unset SOMETHINGIMADEUP\n')
      ed = env_dir(tmp_dir)
      self.assertEqual( [ '1.sh', '2.sh', '3.sh', '4.sh', '5.sh', '6.sh' ], ed.files() )
      self.assertEqual( [
        ( 'BAR', 'orange', action.SET ),
        ( 'FOO', 'kiwi', action.SET ),
        ( 'PATH', '/a/bin', action.PATH_PREPEND ),
        ( 'PATH', '/b/bin', action.PATH_PREPEND ),
        ( 'PATH', '/my/path', action.PATH_REMOVE ),
        ( 'PATH', '/x/bin', action.PATH_APPEND ),
        ( 'PATH', '/y/bin', action.PATH_APPEND ),
        ( 'SOMETHINGIMADEUP', None, action.UNSET ),
      ], ed.instructions() )

      self.assertEqual( {
        'BAR': 'orange',
        'FOO': 'kiwi',
        'PATH': '/b/bin:/a/bin:/x/bin:/y/bin',
      }, ed.transform_env({}) )
        
      self.assertEqual( {
        'BAR': 'orange',
        'FOO': 'kiwi',
        'PATH': '/b/bin:/a/bin:/x/bin:/y/bin',
      }, ed.transform_env({ 'SOMETHINGIMADEUP': 'yes' }) )
        
      self.assertEqual( {
        'BAR': 'orange',
        'FOO': 'kiwi',
        'PATH': '/b/bin:/a/bin:/usr/local/bin:/usr/foo/bin:/x/bin:/y/bin',
      }, ed.transform_env({ 'PATH': '/usr/local/bin:/usr/foo/bin' }) )
        
    finally:
      os.environ['PATH'] = save_path

if __name__ == '__main__':
  unit_test.main()
