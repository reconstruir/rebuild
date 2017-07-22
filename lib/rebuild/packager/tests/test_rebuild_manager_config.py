#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import unittest
from bes.fs import tar_util, temp_file
from rebuild import build_target, System
from rebuild.packager import rebuild_manager_config

class test_rebuild_manager_config(unittest.TestCase):

  TEST_CONFIG_INI = '''
[common]
something1: foo
something2: bar

[project1]
description: project1 config
packages: common1 common2 common3 common4
packages.macos: macos1 macos2
packages.linux: linux1 linux2

[project2]
description: project2 config
packages: common10 common20
'''
  
  def __make_test_config(self, content):
    return temp_file.make_temp_file(content = content)

  def test_load_file(self):
    tmp_config_filename = self.__make_test_config(self.TEST_CONFIG_INI)
    config = rebuild_manager_config()

    config.load_file(tmp_config_filename, build_target(System.MACOS))
    self.assertEqual( [ 'common1', 'common2', 'common3', 'common4', 'macos1', 'macos2' ], config['project1']['packages'] )
    self.assertEqual( 'project1 config', config['project1']['description'] )

    self.assertEqual( [ 'common10', 'common20' ], config['project2']['packages'] )
    self.assertEqual( 'project2 config', config['project2']['description'] )

    config.load_file(tmp_config_filename, build_target(System.LINUX))
    self.assertEqual( [ 'common1', 'common2', 'common3', 'common4', 'linux1', 'linux2' ], config['project1']['packages'] )
    self.assertEqual( 'project1 config', config['project1']['description'] )

    config.load_file(tmp_config_filename, build_target(System.ANDROID))
    self.assertEqual( [ 'common1', 'common2', 'common3', 'common4' ], config['project1']['packages'] )
    self.assertEqual( 'project1 config', config['project1']['description'] )

    config.load_file(tmp_config_filename, build_target(System.IOS))
    self.assertEqual( [ 'common1', 'common2', 'common3', 'common4' ], config['project1']['packages'] )
    self.assertEqual( 'project1 config', config['project1']['description'] )
    
if __name__ == '__main__':
  unittest.main()
