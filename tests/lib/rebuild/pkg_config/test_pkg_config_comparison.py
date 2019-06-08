#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test

import os.path as path
from rebuild.pkg_config.pkg_config import pkg_config
from rebuild.pkg_config.caca_pkg_config import caca_pkg_config

class test_pkg_config_comparison(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/pkg_config'

  @property
  def pc_path(self):
    return [ self.data_dir(where = 'real_examples') ]
 
  @property
  def pc_path_deps(self):
    return [ self.data_dir(where = 'dependency_tests') ]

  @classmethod
  def _list_all_old(clazz, p):
    return pkg_config.list_all(p)
  
  @classmethod
  def _list_all_new(clazz, p):
    return [ ( item.name, item.description ) for item in caca_pkg_config(p).list_all() ]
  
  @classmethod
  def _list_all_names_old(clazz, p):
    return [ item[0] for item in clazz._list_all_old(p) ]
  
  @classmethod
  def _list_all_names_new(clazz, p):
    return [ item[0] for item in clazz._list_all_new(p) ]
  
  def test_list_all_names(self):
    rnew = self._list_all_names_new(self.pc_path_deps)
    rold = self._list_all_names_old(self.pc_path_deps)
    self.assertEqual( rold, rnew )

  def xtest_cflags(self):
    all_mod = self._list_all_names_new(self.pc_path_deps)
    for mod in all_mod:
      cnew = caca_pkg_config(self.pc_path).cflags(mod)
      #cnew = pkg_config.cflags(mod, self.pc_path_deps)
      cold = pkg_config.cflags(mod, self.pc_path_deps)
      self.assertEqual( cold, cnew )

  def xtest_modversion(self):
    pc = caca_pkg_config(self.pc_path)
    mod_versions = [ pc.module_version(module_name) for module_name in self.ALL_MODULES ]
    expected_versions = [
      '0.24', '18.0.12', '2.0.0', '2.44.1', '2.44.1', '2.44.1', '2.44.1', '2.44.1',
      '2.44.1', '2.44.1', '2.44.1', '2.2.0', '6.9.2', '6.9.2', '6.9.2', '6.9.2',
      '1.72', '3.1.2', '56.41.100', '56.4.100', '5.16.101', '56.36.100', '54.27.100',
      '1.0.2d', '7.44.0', '3.2.1', '1.6.18', '1.6.18', '1.0.2d', '1.2.100', '3.1.101',
      '4.0.4', '0.4.3', '2.9.2', '6.9.2', '6.9.2', '6.9.2', '6.9.2', '6.9.2', '6.9.2',
      '3.0.0', '2.2.0', '1.0.2d', '3.02.02', '6.9.2', '6.9.2', '1.2.8',
    ]
    self.assertEquals( expected_versions, mod_versions )
    
  def xtest_dependencies(self):
    pc = caca_pkg_config(self.pc_path_deps)
    print(pc.dep_map)
    all_modules = pc.list_all_names()
    for m in all_modules:
      reqs = pc.module_requires(m)
      print('%s: %s' % (m, reqs))
    
if __name__ == '__main__':
  unit_test.main()
