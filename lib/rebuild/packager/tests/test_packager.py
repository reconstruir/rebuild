#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from rebuild import build_target
from rebuild.packager import build_script, packager, rebuild_config, rebuild_env
from bes.archive import archiver
from rebuild.packager.unit_test_packaging import unit_test_packaging
from rebuild.source_finder import local_source_finder, source_finder_chain

class test_packager(unit_test):

  __unit_test_data_dir__ = 'test_data/packager'

  DEBUG = False
#  DEBUG = True
  
  def test_amhello(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tmp_source_dir = path.join(tmp_dir, 'source')
    rebuildfile = path.join(tmp_source_dir, 'build_amhello.py')
    script_content = unit_test_packaging.make_build_script_content('amhello', '1.0', 0)
    file_util.save(rebuildfile, content = script_content)

    bt = build_target()
    script = build_script.load_build_scripts(rebuildfile, bt)[0]
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    config = rebuild_config()
    config.build_root = path.join(tmp_dir, 'BUILD')
    config.no_network = True
    config.source_dir = self.data_dir()
    env = rebuild_env(config, [ rebuildfile ])
    pkg = packager(script, env)
    result = pkg.execute()
    self.assertTrue( result.success )
    output = result.output
    artifact_path = output['published_tarball']
    self.assertTrue( path.exists(artifact_path) )

    metadata = archiver.extract_member_to_string(artifact_path, 'metadata/info.json')
    # FIXME: check the metadata
    
if __name__ == '__main__':
  unit_test.main()
