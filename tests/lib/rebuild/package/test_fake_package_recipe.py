#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.package.fake_package_recipe import fake_package_recipe as R
from rebuild.package import artifact_descriptor as AD
from rebuild.base import requirement_list as RL

#import os.path as path, unittest
from bes.fs import temp_file, temp_item
#from bes.archive import archiver, temp_archive
#from rebuild.base import build_level, build_target, build_system, build_version, package_descriptor, requirement, requirement_list
#rom rebuild.package.package import package
#from rebuild.package.unit_test_packages import unit_test_packages

class test_fake_package_recipe(unit_test):

  DEBUG = False
  #DEBUG = True

  def test___str__(self):

    AD('foo', '1.2.3', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18')
    r = R(AD('foo', '1.2.3', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
          [
            temp_item('bin/foo.sh', '#!/bin/bash\necho foo\nexit 0\n', 0o755),
            temp_item('bin/bar.sh', '#!/bin/bash\necho bar\nexit 1\n', 0o755),
          ],
          [
            temp_item('foo_env.sh', '#@REBUILD_HEAD@\nexport FOO_ENV=foo\n', 0x644),
            temp_item('bar_env.sh', '#@REBUILD_HEAD@\nexport BAR_ENV=bar\n', 0x644),
          ],
          RL.parse('apple >= 1.2.3 orange >= 6.6.6'),
          { 'prop1': 5, 'prop2': 'hi' }
          )
    expected = '''fake_package
  metadata
    name foo
    version 1.2.3
    revision 0
    epoch 0
    system linux
    level release
    arch ('x86_64',)
    distro ubuntu
    distro_version 18


  requirements
    all: apple >= 1.2.3
    all: orange >= 6.6.6

  properties
    prop1=5
    prop2=hi'''    
    self.assertMultiLineEqual( expected, str(r) )
    
if __name__ == '__main__':
  unit_test.main()
