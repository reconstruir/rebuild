#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
import os.path as path
from bes.fs.temp_file import temp_file
from rebuild.base import build_target, package_descriptor, requirement
from rebuild.builder import builder_script, builder_script_manager, builder_config, builder_env

class test_builder_script(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/builder_script'

  @classmethod
  def setUpClass(clazz):
    unit_test.raise_skip('broken')
  
  def test_zlib(self):
    filename = self.data_path('build_zlib.rebc')
    script = self._load_builder_script(filename)
    expected_requirements = []
    expected_properties = {}
    self.assertEqual( package_descriptor('zlib', '1.2.8-1', requirements = expected_requirements, properties = expected_properties).__dict__, script.descriptor.__dict__ )
    self.assertEqual( [], script.descriptor.requirements )

  def test_libjpeg(self):
    filename = self.data_path('build_libjpeg.rebc')
    script = self._load_builder_script(filename)
    expected_requirements = []
    expected_properties = {}
    self.assertEqual( package_descriptor('libjpeg', '9a-1', requirements = expected_requirements, properties = expected_properties), script.descriptor )
    self.assertEqual( [], script.descriptor.requirements )

  def test_libopenjpeg(self):
    filename = self.data_path('build_libopenjpeg.rebc')
    script = self._load_builder_script(filename)

    expected_requirements = requirement.parse('cmake(all) >= 3.3.1-1')
    expected_properties = {}
    expected_package_info = package_descriptor('libopenjpeg', '2.1-1',
                                               requirements = expected_requirements,
                                               properties = expected_properties)
    self.assertEqual( expected_package_info, script.descriptor )
    self.assertEqual( expected_requirements, script.descriptor.requirements )

  def test_libpng(self):
    filename = self.data_path('rebuild.recipe')
    script = self._load_builder_script(filename)

    expected_requirements = requirement.parse('zlib(all) >= 1.2.8-1')
    expected_properties = {}
    expected_package_info = package_descriptor('libpng', '1.6.18-1',
                                               requirements = expected_requirements,
                                               properties = expected_properties)

    self.assertEqual( expected_package_info, script.descriptor )
    self.assertEqual( expected_requirements, script.descriptor.requirements )

  def _load_builder_script(self, filename):
    bt = build_target()
    config = builder_config()
    config.build_root = temp_file.make_temp_dir()
    config.no_network = True
    config.no_checksums = True
    config.source_dir = path.dirname(filename)
    config.verbose = True
    env = builder_env(config, [ filename ])
    sm = builder_script_manager([ filename ], bt, env)
    self.assertEqual( 1, len(sm.scripts) )
    return sm.scripts.values()[0]
    
if __name__ == '__main__':
  unit_test.main()
