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
          temp_item('bin/tfoo.py', '#!/usr/bin/env python\nprint(\'foo\')\nraise SystemExit(0)\n', 0o755),
          temp_item('bin/tbar.py', '#!/usr/bin/env python\nprint(\'bar\')\nraise SystemExit(0)\n', 0o755),
        ],
        [
          temp_item('tfoo.sh', 'export TFOO_ENV1=tfoo_env1\n', 0o644),
          temp_item('tbar.sh', 'export TBAR_ENV1=tbar_env1\n', 0o644),
        ],
        RL.parse(''), #apple >= 1.2.3 orange >= 6.6.6'),
        { }, # 'prop1': 5, 'prop2': 'hi' }
      )
    content = '''
fake_package
  metadata
    name = foo
    version = 1.2.3
    revision = 0
    epoch = 0
    system = linux
    level = release
    arch = x86_64
    distro = ubuntu
    distro_version = 18
  
  files
    bin/tfoo.py
      \#!/usr/bin/env python
      print('foo')
      raise SystemExit(0)

    bin/tbar.py
      \#!/usr/bin/env python
      print('bar')
      raise SystemExit(0)

  env_files
    tfoo_env.sh
      export TFOO_ENV1=tfoo_env1

  env_files
    tbar_env.sh
      export TBAR_ENV1=tbar_env1
'''
    actual = self._parse(content)
    self.assertEqual( recipe.metadata, actual[0].metadata )
    self.assertEqual( recipe.properties, actual[0].properties )
    self.assertEqual( recipe.requirements, actual[0].requirements )
    print('expected: %s' % (str(recipe.files)))
    print('  actual: %s' % (str(actual[0].files)))
    self.assertEqual( recipe.files, actual[0].files )
#    self.assertEqual( recipe.env_files, actual[0].env_files )

  @classmethod
  def _parse(self, text, starting_line_number = 0):
    return P(path.basename(__file__), text, starting_line_number = starting_line_number).parse()
    
if __name__ == '__main__':
  unit_test.main()
