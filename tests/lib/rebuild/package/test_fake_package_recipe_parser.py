#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.unit_test import unit_test
from rebuild.package.fake_package_recipe import fake_package_recipe as R
from rebuild.package.fake_package_recipe_parser import fake_package_recipe_parser as P
from rebuild.package import artifact_descriptor as AD
from rebuild.base import requirement_list as RL

from bes.fs import temp_file, temp_item

class test_fake_package_recipe_parser(unit_test):

  DEBUG = False
  DEBUG = True

  def test_parse(self):
    recipe = \
      R(AD('foo', '1.2.3', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
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
    content = '''
fake_package
  metadata
    name tool_foo
    version 1.2.3
    revision 0
    epoch 0
    system linux
    level release
    arch x86_64
    distro ubuntu
    distro_version 18
  
  files
    bin/tfoo.py
      #!/usr/bin/env python
      print('foo')
      raise SystemExit(0)

  env_files
    tfoo_env.sh
      export TFOO_ENV1=tfoo_env1
'''

    self.assertEqual( [ recipe ], self._parse(content) )

  @classmethod
  def _parse(self, text, starting_line_number = 0):
    return P(path.basename(__file__), text, starting_line_number = starting_line_number).parse()
    
if __name__ == '__main__':
  unit_test.main()
