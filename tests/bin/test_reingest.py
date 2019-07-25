#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.archive.temp_archive import temp_archive
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.testing.script_unit_test import script_unit_test
from bes.testing.unit_test_skip import raise_skip
from bes.web.file_web_server_tester import file_web_server_tester

class test_reingest(script_unit_test):

  __script__ = __file__, '../../bin/reingest.py'

  @classmethod
  def setUpClass(clazz):
    #raise_skip('work in progress not ready')
    pass
  
  def test_http(self):

    project_file_content = '''\
!rebuild.ingest.v1!

description
  Third party libraries and tools needed by ego_automation

#variables
#  PYHOSTED_HOME_URL=https://files.pythonhosted.org/packages
#  PYTHON_PACKAGES_TARGET_DIR=python/packages

entry libfoo 1.2.3

  data
    all: checksum 1.2.3 {checksum}
    #all: checksum 0.2.2 4a9100ab61047fd9bd395bcef3ce5403365cafd55c1e0d0299cde14958e47be9

  variables
    all: _home_url={url_base}/downloads
    all: _upstream_name=foo
    all: _upstream_filename=${{_upstream_name}}-${{VERSION}}.tar.gz
    all: _filename=${{_upstream_name}}-${{VERSION}}.tar.gz
    all: _ingested_filename=lib/${{_filename}}
    
  method http
    all: url=${{_home_url}}/${{_filename}}
    all: checksum=@{{DATA:checksum:${{VERSION}}}}
    all: ingested_filename=${{_ingested_filename}}
'''

    fs_config_file_content = '''\
fsconfig
  fs_type: fs_local
  where: {tmp_dir}/downloads
  cache_dir: {tmp_dir}/cache
'''
    tmp_dir = self.make_temp_dir()
    tester = file_web_server_tester(root_dir = tmp_dir)
    tester.write_archive('downloads/foo-1.2.3.tar.gz', [
      temp_archive.item('apple.txt', content = 'apple.txt\n'),
      temp_archive.item('orange.txt', content = 'orange.txt\n'),
    ])
    tester.start()
    url = tester.make_url('foo.txt')

    project_file_formatted = project_file_content.format(url_base = tester.make_url(),
                                                         checksum = tester.file_checksum('downloads/foo-1.2.3.tar.gz'))
    tmp_project_file = temp_file.make_temp_file(content = project_file_formatted)
    tmp_fs_dir = self.make_temp_dir(suffix = '.fs')
    fs_config_file_content_formatted = fs_config_file_content.format(tmp_dir = tmp_fs_dir)
    tmp_fs_config_file = temp_file.make_temp_file(content = fs_config_file_content_formatted)
    tmp_cache_dir = self.make_temp_dir(suffix = '.cache')

    args = [
      'run',
      '--cache-dir', tmp_cache_dir,
      tmp_project_file,
      tmp_fs_config_file,
    ]
    
    rv = self.run_script(args)
    if self.DEBUG:
      print(rv.output)
    self.assertEqual( 0, rv.exit_code )

    self.assertEqual( [
      'downloads/lib/foo-1.2.3.tar.gz',
    ], file_find.find(tmp_fs_dir) )
    
    tester.stop()
  
if __name__ == '__main__':
  script_unit_test.main()
