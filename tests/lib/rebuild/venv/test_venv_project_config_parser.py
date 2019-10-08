#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from bes.testing.unit_test import unit_test
from rebuild.recipe.variable_manager import variable_manager
from rebuild.venv.venv_project_config_parser import venv_project_config_parser as P
from rebuild.recipe.recipe_error import recipe_error as ERR
from rebuild.base.build_target import build_target
from bes.key_value.key_value import key_value as KV
from bes.key_value.key_value_list import key_value_list as KVL
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

class test_venv_parser(unit_test):

  @classmethod
  def _parse(self, text, starting_line_number = 0, variables = None):
    vm = variable_manager()
    if variables:
      vm.add_variables(KVL.parse(variables))
    return P(path.basename(__file__), text, starting_line_number = starting_line_number).parse(vm)

  def test_invalid_magic(self):
    with self.assertRaises(ERR) as context:
      self._parse('nomagic')

  def test_name(self):
    text = '''!rebuild.revenv!
projects
  foo
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p.projects) )
    self.assertEqual( 'foo', p.projects[0].name )

  def test_description(self):
    text = '''!rebuild.revenv!
projects
  foo
    description
      foo is nice
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p.projects) )
    self.assertEqual( 'foo', p.projects[0].name )
    self.assertEqual( 'foo is nice', p.projects[0].description )
    
  def test_description(self):
    text = '''!rebuild.revenv!
projects
  foo
    description
      foo is nice
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p.projects) )
    self.assertEqual( 'foo', p.projects[0].name )
    self.assertEqual( 'foo is nice', p.projects[0].description )
    
  def test_variables(self):
    text = '''!rebuild.revenv!
projects
  foo
    variables
      all: FOO=hi BAR=666
      linux: AUTHOR=linus
      macos: AUTHOR=apple
'''

    p = self._parse(text)
    self.assertEqual( 1, len(p.projects) )
    self.assertEqual( [ KV('FOO', 'hi'), KV('BAR', '666'), KV('AUTHOR', 'linus') ], p.projects[0].resolve_variables('linux') )
    self.assertEqual( [ KV('FOO', 'hi'), KV('BAR', '666'), KV('AUTHOR', 'apple') ], p.projects[0].resolve_variables('macos') )
    
  def test_packages(self):
    text = '''!rebuild.revenv!
projects
  foo
    packages
      forall1 == 1.1.1
      all: forall2 >= 1.2
      linux: forlinux1 >= 2.2
      macos: formacos1 >= 3.3
      forall3 >= 5.5
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p.projects) )
    self.assertEqual( [
      ( 'forall1', '==', '1.1.1', 'all', None, None ),
      ( 'forall2', '>=', '1.2', 'all', None, None ),
      ( 'forlinux1', '>=', '2.2', 'linux', None, None ),
      ( 'forall3', '>=', '5.5', 'all', None, None ),
    ], p.projects[0].resolve_packages('linux') )

    self.assertEqual( [
      ( 'forall1', '==', '1.1.1', 'all', None, None ),
      ( 'forall2', '>=', '1.2', 'all', None, None ),
      ( 'formacos1', '>=', '3.3', 'macos', None, None ),
      ( 'forall3', '>=', '5.5', 'all', None, None ),
    ], p.projects[0].resolve_packages('macos') )

    self.assertEqual( [
      ( 'forall1', '==', '1.1.1', 'all', None, None ),
      ( 'forall2', '>=', '1.2', 'all', None, None ),
      ( 'forall3', '>=', '5.5', 'all', None, None ),
    ], p.projects[0].resolve_packages('android') )

  def test_packages_dups(self):
    text = '''!rebuild.revenv!
projects
  foo
    packages
      kiwi
      orange
      apple
      kiwi
'''
    with self.assertRaises(ERR) as context:
      self._parse(text)

  def test_packages_dups_multiple_sections(self):
    text = '''!rebuild.revenv!
projects
  foo
    packages
      orange
      apple
      kiwi
    packages
      kiwi
'''
    with self.assertRaises(ERR) as context:
      self._parse(text)

  def test_python_code(self):
    text = '''!rebuild.revenv!
projects
  foo
    python_code
      > print('hello from python_code inside a venv')
        print('hello again')
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p.projects) )
    expected = '''\
print('hello from python_code inside a venv')
print('hello again')'''
    self.assertMultiLineEqual( expected, p.projects[0].python_code)

  def test_storage_config(self):
    text = '''!rebuild.revenv!
config
  storage
    name: test_local
    provider: local
    location: /tmp/loc
    repo: foo
    root_dir: bar
  
  storage
    name: test_pcloud
    provider: pcloud
    location:
    repo: foo
    root_dir: bar
    download.username: fred
    download.password: flintpass
    upload.username: fred
    upload.password: flintpass
  
  storage
    name: test_artifactory
    provider: artifactory
    location: https://mycorp.jfrog.io/mycorp
    repo: foo
    root_dir: bar
    download.username: fred
    download.password: flintpass
    upload.username: admin
    upload.password: sekret
projects
  foo
'''
    p = self._parse(text)
    t = p.storage_config.get('test_local')
    self.assertEqual( 'test_local', t.name )
    self.assertEqual( 'local', t.provider )
    self.assertEqual( '/tmp/loc', t.location )
    self.assertEqual( 'foo', t.repo )
    self.assertEqual( 'bar', t.root_dir )
    self.assertEqual( '', t.download.username )
    self.assertEqual( '', t.download.password )
    self.assertEqual( '', t.upload.username )
    self.assertEqual( '', t.upload.password )

    t = p.storage_config.get('test_pcloud')
    self.assertEqual( 'test_pcloud', t.name )
    self.assertEqual( 'pcloud', t.provider )
    self.assertEqual( '', t.location )
    self.assertEqual( 'foo', t.repo )
    self.assertEqual( 'bar', t.root_dir )
    self.assertEqual( 'fred', t.download.username )
    self.assertEqual( 'flintpass', t.download.password )
    self.assertEqual( 'fred', t.upload.username )
    self.assertEqual( 'flintpass', t.upload.password )
    
    t = p.storage_config.get('test_artifactory')
    self.assertEqual( 'test_artifactory', t.name )
    self.assertEqual( 'artifactory', t.provider )
    self.assertEqual( 'https://mycorp.jfrog.io/mycorp', t.location )
    self.assertEqual( 'foo', t.repo )
    self.assertEqual( 'bar', t.root_dir )
    self.assertEqual( 'fred', t.download.username )
    self.assertEqual( 'flintpass', t.download.password )
    self.assertEqual( 'admin', t.upload.username )
    self.assertEqual( 'sekret', t.upload.password )

  def test_empty_projects(self):
    text = '''!rebuild.revenv!
projects
'''
    p = self._parse(text)
    self.assertEqual( 0, len(p.projects) )

  def test_use_variables(self):
    text = '''!rebuild.revenv!
projects
  foo
    variables
      all: GUAVA_VERSION=6.0.0
      linux: KIWI_VERSION=1.0.0
      macos: KIWI_VERSION=9.0.0
      linux: ORANGE_VERSION=3.0.0
      macos: ORANGE_VERSION=7.0.0
      linux: LEMON_VERSION=2.0.0
      macos: PLUM_VERSION=5.0.0

    packages
      guava == ${GUAVA_VERSION}
      kiwi == ${KIWI_VERSION}
      orange == ${ORANGE_VERSION}
      linux: lemon == ${LEMON_VERSION}
      macos: plum == ${PLUM_VERSION}
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p.projects) )
    self.assertEqual( [
      ( 'guava', '==', '6.0.0', 'all', None, None ),
      ( 'kiwi', '==', '1.0.0', 'all', None, None ),
      ( 'orange', '==', '3.0.0', 'all', None, None ),
      ( 'lemon', '==', '2.0.0', 'linux', None, None ),
    ], p.projects[0].resolve_packages('linux') )
    return
    self.assertEqual( [
      ( 'guava', '==', '6.0.0', 'all', None, None ),
      ( 'kiwi', '==', '9.0.0', 'all', None, None ),
      ( 'orange', '==', '7.0.0', 'all', None, None ),
      ( 'plum', '==', '5.0.0', 'macos', None, None ),
    ], p.projects[0].resolve_packages('macos') )
    
  def test_use_env_vars(self):
    text = '''!rebuild.revenv!
projects
  foo
    variables
      all: GUAVA_VERSION=6.0.0
      linux: KIWI_VERSION=1.0.0
      macos: KIWI_VERSION=9.0.0

    packages
      guava == ${GUAVA_VERSION}
      kiwi == ${KIWI_VERSION}
'''
    try:
      os.environ['GUAVA_VERSION'] = '6.6.6'
      os.environ['KIWI_VERSION'] = '7.7.7'
      p = self._parse(text)
      self.assertEqual( 1, len(p.projects) )
      self.assertEqual( [
        ( 'guava', '==', '6.6.6', 'all', None, None ),
        ( 'kiwi', '==', '7.7.7', 'all', None, None ),
      ], p.projects[0].resolve_packages('linux') )
      self.assertEqual( [
        ( 'guava', '==', '6.6.6', 'all', None, None ),
        ( 'kiwi', '==', '7.7.7', 'all', None, None ),
      ], p.projects[0].resolve_packages('macos') )
    finally:
      del os.environ['GUAVA_VERSION']
      del os.environ['KIWI_VERSION']
    
  def test_use_variable_manager(self):
    text = '''!rebuild.revenv!
projects
  foo
#    variables
#      all: GUAVA_VERSION=6.0.0
#      linux: KIWI_VERSION=1.0.0
#      macos: KIWI_VERSION=9.0.0

    packages
      guava == ${GUAVA_VERSION}
      kiwi == ${KIWI_VERSION}
'''
    p = self._parse(text, variables = 'GUAVA_VERSION=9.9.9 KIWI_VERSION=7.7.7')
    self.assertEqual( 1, len(p.projects) )
    self.assertEqual( [
      ( 'guava', '==', '9.9.9', 'all', None, None ),
      ( 'kiwi', '==', '7.7.7', 'all', None, None ),
    ], p.projects[0].resolve_packages('linux') )
    self.assertEqual( [
      ( 'guava', '==', '9.9.9', 'all', None, None ),
      ( 'kiwi', '==', '7.7.7', 'all', None, None ),
    ], p.projects[0].resolve_packages('macos') )
    
  def test_use_variable_manager_overrides_project_variables(self):
    text = '''!rebuild.revenv!
projects
  foo
    variables
      all: GUAVA_VERSION=6.0.0
      linux: KIWI_VERSION=1.0.0
      macos: KIWI_VERSION=9.0.0

    packages
      guava == ${GUAVA_VERSION}
      kiwi == ${KIWI_VERSION}
'''
    p = self._parse(text, variables = 'GUAVA_VERSION=9.9.9 KIWI_VERSION=7.7.7')
    self.assertEqual( 1, len(p.projects) )
    self.assertEqual( [
      ( 'guava', '==', '9.9.9', 'all', None, None ),
      ( 'kiwi', '==', '7.7.7', 'all', None, None ),
    ], p.projects[0].resolve_packages('linux') )
    self.assertEqual( [
      ( 'guava', '==', '9.9.9', 'all', None, None ),
      ( 'kiwi', '==', '7.7.7', 'all', None, None ),
    ], p.projects[0].resolve_packages('macos') )
    
  def _filename_for_parser(self):
    'Return a fake filename for parser.  Some values need it to find files relatively to filename.'
    return self.data_path('whatever')
  
if __name__ == '__main__':
  unit_test.main()
