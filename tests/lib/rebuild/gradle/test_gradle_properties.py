#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.unit_test import unit_test
from bes.fs.temp_file import temp_file

from rebuild.gradle.gradle_properties import gradle_properties as GP

class test_gradle_properties(unit_test):

  def test_basic(self):
    content = '''\
devUser=fred@flintstone.com
devPassword=flintpass
systemProp.gradle.wrapperUser=tuser
systemProp.gradle.wrapperPassword=tpassword
'''
    g = GP(temp_file.make_temp_file(content = content))
    self.assertEqual( {
      'devUser': 'fred@flintstone.com',
      'devPassword': 'flintpass',
      'systemProp.gradle.wrapperUser': 'tuser',
      'systemProp.gradle.wrapperPassword': 'tpassword',
    }, g.values )
    c = g.credentials('dev')
    self.assertEqual( 'fred@flintstone.com', c.username )
    self.assertEqual( 'flintpass', c.password )
    c = g.credentials('systemProp.gradle.wrapper')
    self.assertEqual( 'tuser', c.username )
    self.assertEqual( 'tpassword', c.password )
    
if __name__ == '__main__':
  unit_test.main()
