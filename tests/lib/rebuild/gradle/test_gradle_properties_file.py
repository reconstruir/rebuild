#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file

from rebuild.gradle.gradle_properties_file import gradle_properties_file as GPL

class test_gradle_properties_file(unit_test):

  def test_read(self):
    content = '''\
devUser=fred@flintstone.com
devPassword=flintpass
systemProp.gradle.wrapperUser=tuser
systemProp.gradle.wrapperPassword=tpassword
'''
    tmp_file = temp_file.make_temp_file(content = content)
    p = GPL.read(tmp_file)
    self.assertEqual( {
      'devUser': 'fred@flintstone.com',
      'devPassword': 'flintpass',
      'systemProp.gradle.wrapperUser': 'tuser',
      'systemProp.gradle.wrapperPassword': 'tpassword',
    }, GPL.read(tmp_file) )
    
if __name__ == '__main__':
  unit_test.main()
