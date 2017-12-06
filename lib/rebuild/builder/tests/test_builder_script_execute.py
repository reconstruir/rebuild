#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path, json
from bes.testing.unit_test import unit_test
from bes.system import host
from bes.fs import file_util, temp_file
from rebuild.base import build_target
from rebuild.builder import builder_script, builder_script_manager, builder_config, builder_env
from bes.archive import archiver
from rebuild.builder.unit_test_packaging import unit_test_packaging
from rebuild.source_finder import local_source_finder, source_finder_chain

class test_builder_script_execute(unit_test):

  __unit_test_data_dir__ = '../../test_data/packager'

  DEBUG = False
#  DEBUG = True

  @classmethod
  def setUpClass(clazz):
    unit_test.raise_skip('broken')
  
  def test_amhello(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tmp_source_dir = path.join(tmp_dir, 'source')
    rebuildfile = path.join(tmp_source_dir, 'build_amhello.py')
    script_content = unit_test_packaging.make_recipe_v1_content('amhello', '1.0', 0)
    file_util.save(rebuildfile, content = script_content)
    bt = build_target()
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    config = builder_config()
    config.build_root = path.join(tmp_dir, 'BUILD')
    config.no_network = True
    config.source_dir = self.data_dir()
    env = builder_env(config, [ rebuildfile ])
    script = self._load_builder_script(rebuildfile)
    result = script.execute({})
    self.assertTrue( result.success )
    output = result.output
    artifact_path = output['published_tarball']
    self.assertTrue( path.exists(artifact_path) )
    self.assertEqual( [
      'files/bin/hello',
      'files/bin/rebbe_hello',
      'files/share/doc/amhello/README',
      'metadata/info.json'
    ], archiver.members(artifact_path) )
    self.assertEqual( {
      u'archs': [u'x86_64'],
      u'build_requirements': [],
      u'build_level': u'release',
      u'name': u'amhello',
      u'properties': {u'category': u'lib'},
      u'requirements': [],
      u'system': u''+host.SYSTEM,
      u'version': u'1.0'
    }, json.loads(archiver.extract_member_to_string(artifact_path, 'metadata/info.json')) )

  def _load_builder_script(self, filename):
    bt = build_target()
    config = builder_config()
    config.build_root = temp_file.make_temp_dir()
    config.no_network = True
    config.no_checksums = True
    config.source_dir = path.dirname(filename)
    config.verbose = True
    env = builder_env(config, [ filename ])
    sm = builder_script_manager([ filename ], env)
    self.assertEqual( 1, len(sm.scripts) )
    return sm.scripts.values()[0]
    
if __name__ == '__main__':
  unit_test.main()
