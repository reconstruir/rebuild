#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.archive.temp_archive import temp_archive
from bes.fs.file_find import file_find
from bes.system.execute import execute
from bes.archive.archiver import archiver
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.testing.program_unit_test import program_unit_test
from bes.web.file_web_server_tester import file_web_server_tester

class test_reb_ingest(program_unit_test):

  _PROGRAM = program_unit_test.resolve_program(__file__, '..', '..', 'bin', 'reb.py')

  def test_http(self):

    project_file_content = '''\
!rebuild.ingest.v1!
entry libfoo 1.2.3

  data
    all: checksum 1.2.3 {checksum}

  variables
    all: _home_url={url_base}/downloads
    all: _filename=foo-${{VERSION}}.tar.gz
    all: _ingested_filename=lib/${{NAME}}-${{VERSION}}.tar.gz
    
  method http
    all: url=${{_home_url}}/${{_filename}}
    all: checksum=@{{DATA:checksum:${{VERSION}}}}
    all: ingested_filename=${{_ingested_filename}}
'''

    vfs_config_file_content = '''\
fsconfig
  vfs_type: local
  vfs_class_path: bes.vfs.vfs_local
  local_root_dir: {tmp_dir}/downloads
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
    tmp_project_dir = temp_file.make_temp_dir(suffix = '.project.dir')
    tmp_project_filename = file_util.save(path.join(tmp_project_dir, 'test.reingest'),
                                          content = project_file_formatted)
    tmp_fs_local_root_dir = self.make_temp_dir(suffix = '.fs.local.root.dir')
    vfs_config_file_content_formatted = vfs_config_file_content.format(tmp_dir = tmp_fs_local_root_dir)
    tmp_vfs_config_file = temp_file.make_temp_file(content = vfs_config_file_content_formatted, suffix = '.config.fs')
    tmp_cache_dir = self.make_temp_dir(suffix = '.cache.dir')

    args = [
      'ingest',
      'run',
      '--cache-dir', tmp_cache_dir,
      tmp_vfs_config_file,
      tmp_project_dir,
    ]
    
    rv = self.run_program(self._PROGRAM, args)
    if self.DEBUG:
      print(rv.output)
    self.assertEqual( 0, rv.exit_code )

    self.assertEqual( [
      'downloads/lib/libfoo-1.2.3.tar.gz',
    ], file_find.find(tmp_fs_local_root_dir) )

    tester.stop()
  
  def test_http_with_arcname(self):

    project_file_content = '''\
!rebuild.ingest.v1!
entry foo 1.2.3

  data
    all: checksum 1.2.3 {checksum}

  variables
    all: _home_url={url_base}/something
    all: _filename=foo-${{VERSION}}.py
    
  method http
    all: url=${{_home_url}}/${{_filename}}
    all: checksum=@{{DATA:checksum:${{VERSION}}}}
    all: ingested_filename=something/${{NAME}}-${{VERSION}}.tar.gz
    all: arcname=bin/foo.py
'''

    vfs_config_file_content = '''\
fsconfig
  vfs_type: local
  vfs_class_path: bes.vfs.vfs_local
  local_root_dir: {tmp_dir}/stuff
'''
    file_content = '''\
#!/usr/bin/env python
print('foo')
'''

    tmp_dir = self.make_temp_dir()
    tester = file_web_server_tester(root_dir = tmp_dir)
    filename = 'something/foo-1.2.3.py'
    tester.write_file(filename, content = file_content, mode = 0o0755)
    tester.start()
    url = tester.make_url(filename)

    project_file_formatted = project_file_content.format(url_base = tester.make_url(),
                                                         checksum = tester.file_checksum(filename))
    tmp_project_dir = temp_file.make_temp_dir(suffix = '.project.dir')
    tmp_project_filename = file_util.save(path.join(tmp_project_dir, 'test.reingest'),
                                          content = project_file_formatted)
    tmp_fs_local_root_dir = self.make_temp_dir(suffix = '.fs.local.root.dir')
    vfs_config_file_content_formatted = vfs_config_file_content.format(tmp_dir = tmp_fs_local_root_dir)
    tmp_vfs_config_file = temp_file.make_temp_file(content = vfs_config_file_content_formatted, suffix = '.config.fs')
    tmp_cache_dir = self.make_temp_dir(suffix = '.cache.dir')

    args = [
      'ingest',
      'run',
      '--cache-dir', tmp_cache_dir,
      tmp_vfs_config_file,
      tmp_project_dir,
    ]
    
    rv = self.run_program(self._PROGRAM, args)
    if self.DEBUG:
      print(rv.output)
    self.assertEqual( 0, rv.exit_code )

    self.assertEqual( [
      'stuff/something/foo-1.2.3.tar.gz',
    ], file_find.find(tmp_fs_local_root_dir) )

    tmp_archive = path.join(tmp_fs_local_root_dir, 'stuff/something/foo-1.2.3.tar.gz')
    
    self.assertEqual( [
      'bin/foo.py',
    ], archiver.members(tmp_archive) )

    tmp_extracted_exe = archiver.extract_member_to_temp_file(tmp_archive, 'bin/foo.py')

    self.assertEqual( 'foo', execute.execute(tmp_extracted_exe).stdout.strip() )
    
    tester.stop()
  
if __name__ == '__main__':
  program_unit_test.main()
