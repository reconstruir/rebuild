#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from rebuild import build_target
from rebuild.packager import build_script, packager, rebuilder_config
from bes.archive import archiver
from rebuild.packager.unit_test_packaging import unit_test_packaging

class test_packager(unit_test):

  __unit_test_data_dir__ = 'test_data/packager'

  DEBUG = False
#  DEBUG = True
  
  def test_amhello(self):

    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tmp_source_dir = path.join(tmp_dir, 'source')
    rebuildfile = path.join(tmp_source_dir, 'build_amhello.py')
    tarball_filename = 'amhello-1.0.tar.gz'
    tarball_path = path.join(tmp_source_dir, tarball_filename)
    file_util.copy(self.data_path('amhello-1.0.tar.gz'), tarball_path)
    script_content = unit_test_packaging.make_build_script_content('amhello', '1.0', 0)
    print(script_content)
    file_util.save(rebuildfile, content = script_content)

    bt = build_target()
    script = build_script.load_build_scripts(rebuildfile, bt)[0]
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)

    publish_dir = path.join(tmp_dir, 'publish_dir')
    working_dir = path.join(tmp_dir, 'working_dir')
    rebbe_root = path.join(tmp_dir, 'rebbe_root')
    
    all_scripts = { script.package_info.name: script }
    args = {
      'tmp_dir': tmp_dir,
      'publish_dir': publish_dir,
      'working_dir': working_dir,
      'rebbe_root': rebbe_root,
    }
    config = rebuilder_config()
    pkg = packager(script, config, all_scripts, **args)
    result = pkg.execute()
    self.assertTrue( result.success )
    output = result.output
    artifact_path = output['published_tarball']
    self.assertTrue( path.exists(artifact_path) )

    metadata = archiver.extract_member_to_string(artifact_path, 'metadata/info.json')

if __name__ == '__main__':
  unit_test.main()
