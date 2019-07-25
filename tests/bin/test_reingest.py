#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from collections import namedtuple

from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.fs.testing.temp_content import temp_content
from bes.system.execute import execute
from bes.system.os_env import os_env
from bes.testing.script_unit_test import script_unit_test
from bes.url.http_download_cache import http_download_cache
from bes.web.file_web_server import file_web_server
from bes.web.web_server_controller import web_server_controller
from bes.testing.unit_test_skip import raise_skip

#from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT
#from _rebuild_testing.fake_package_recipes import fake_package_recipes as RECIPES
#from rebuild.base.build_target import build_target as BT

class test_reingest(script_unit_test):

  __script__ = __file__, '../../bin/reingest.py'

  @classmethod
  def setUpClass(clazz):
    raise_skip('work in progress not ready')
    pass
  
  def test_http(self):
    tmp_dir = self.make_temp_dir()
    items = [
      temp_archive.item('apple.txt', content = 'apple.txt\n'),
      temp_archive.item('orange.txt', content = 'orange.txt\n'),
    ]
    tmp_archive = temp_archive.make_temp_archive(items, 'tar.gz')
    file_util.copy(tmp_archive, path.join(tmp_dir, 'downloads/1.2.3/foo-1.2.3.tar.gz'))
    

    
    config = '''\
!rebuild.ingest.v1!

description
  Third party libraries and tools needed by ego_automation

variables
  PYHOSTED_HOME_URL=https://files.pythonhosted.org/packages
  PYTHON_PACKAGES_TARGET_DIR=python/packages

entry libfoo 1.2.3

  data
    all: checksum 1.2.3 8088e457264a98ba451a90b8661fcb4f9d6f478f7265d48322a196cec2480729
    all: checksum 0.2.2 4a9100ab61047fd9bd395bcef3ce5403365cafd55c1e0d0299cde14958e47be9

  variables
    all: _home_url=http://pyyaml.org/download/libyaml
    all: _upstream_name=yaml
    all: _upstream_filename=${{_upstream_name}}-${{VERSION}}.tar.gz
    all: _filename=${{_upstream_name}}-${{VERSION}}.tar.gz
    all: _ingested_filename=lib/${{_filename}}
    
  method http
    all: url=${{_home_url}}/${{_filename}}
    all: checksum=@{{DATA:checksum:${{VERSION}}}}
    all: ingested_filename=${{_ingested_filename}}
'''
#    test = self._setup_test(config)
#    args = self._make_packages_cmd('print', test.tmp_dir, 'test1')
#    rv = self.run_script(args)
#    self.assertEqual( 0, rv.exit_code )
#    self.assertEqual( [], self._parse_stdout_list(rv.output) )

  @classmethod
  def _make_temp_content(clazz, items):
    tmp_dir = temp_file.make_temp_dir()
    temp_content.write_items(items, tmp_dir)
    return tmp_dir
  
  def test_tarball_server(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "this is foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "this is baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])

    server = web_server_controller(file_web_server)
    server.start(root_dir = tmp_dir)
    port = server.address[1]

    cache = http_download_cache(temp_file.make_temp_dir())

    url = self._make_url(port, 'foo.txt')

    self.assertFalse( cache.has_url(url) )
    self.assertEqual( "this is foo.txt\n", file_util.read(cache.get_url(url), codec = 'utf-8') )
    self.assertTrue( cache.has_url(url) )

    
    
    server.stop()

  @classmethod
  def _make_url(clazz, port, p):
    base = 'http://localhost:%d' % (port)
    return urlparse.urljoin(base, p)
  
if __name__ == '__main__':
  script_unit_test.main()
