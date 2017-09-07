#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.unit_test import unit_test
from bes.fs import temp_file
from rebuild.jail import config_file

class test_config_file(unit_test):

  __TEST_CONFIG_CONTENT = '''
[jail]
description: nice jail
packages:
  orange
#  strawberry
  apple
  kiwi
binaries:
  /bin/bash
[apple]
description: apple desc
include: 
  /foo*
  /bar*
exclude: 
  /baz*
missing:
  /pear
[orange]
description: orange desc
include:
  /usr*
[hooks]
pre:
  ln -s x ${root}/y
  ln -s a ${root}/b
post:
  ln -s c ${root}/d
  ln -s e ${root}/f
cleanup:
  rm -f ${root}/foo
'''
  
  def test_config_file(self):
    tmp_config_file = temp_file.make_temp_file(content = self.__TEST_CONFIG_CONTENT)
    variables = { 'root': 'caca' }
    config = config_file(tmp_config_file, variables)

    self.assertEqual( 'nice jail', config.jail.description )
    self.assertEqual( 3, len(config.jail.packages) )

    self.assertEqual( 'orange', config.jail.packages[0].name )
    self.assertEqual( 'orange desc', config.jail.packages[0].description )
    self.assertEqual( [ '/usr*' ], config.jail.packages[0].include )
    self.assertEqual( None, config.jail.packages[0].exclude )

    self.assertEqual( 'apple', config.jail.packages[1].name )
    self.assertEqual( 'apple desc', config.jail.packages[1].description )
    self.assertEqual( [ '/foo*', '/bar*' ], config.jail.packages[1].include )
    self.assertEqual( [ '/baz*' ], config.jail.packages[1].exclude )
    self.assertEqual( [ '/pear' ], config.jail.packages[1].missing )

    self.assertEqual( 'kiwi', config.jail.packages[2].name )
    self.assertEqual( 'none', config.jail.packages[2].description )
    self.assertEqual( None, config.jail.packages[2].include )
    self.assertEqual( None, config.jail.packages[2].exclude )

    self.assertEqual( [ '/bin/bash' ], config.jail.binaries )

    self.assertEqual( [ 'ln -s x caca/y', 'ln -s a caca/b' ], config.jail.hooks.pre )
    self.assertEqual( [ 'ln -s c caca/d', 'ln -s e caca/f' ], config.jail.hooks.post )
    self.assertEqual( [ 'rm -f caca/foo' ], config.jail.hooks.cleanup )
    
if __name__ == '__main__':
  unit_test.main()
