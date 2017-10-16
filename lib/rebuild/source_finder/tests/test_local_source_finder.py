#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.testing import temp_content
from bes.fs import temp_file
from bes.archive.temp_archive import temp_archive
from rebuild.source_finder import local_source_finder
import os.path as path

class test_local_finder(unit_test):

  def _make_tarball(ext):
    return temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], ext).filename
  
  BZ2_TARBALL = _make_tarball('bz2')
  TAR_GZ_TARBALL = _make_tarball('tar.gz')
  TGZ_TARBALL = _make_tarball('tgz')
  ZIP_TARBALL = _make_tarball('zip')
  
  def test_local_finder(self):
    tmp_source_dir = temp_content.write_items_to_temp_dir([
      'file a/alpha-1.2.3.tar.gz "%s" 644' % (self.TAR_GZ_TARBALL),
      'file b/beta-1.2.3.tar.gz "%s" 644' % (self.TAR_GZ_TARBALL),
    ])
    finder = local_source_finder(tmp_source_dir)
    self.assertEqual( path.join(tmp_source_dir, 'a/alpha-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'linux') )
    
  def test_local_finder_invalid_archive(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
      'file a/alpha-1.2.3.tar.gz "alpha-1.2.3.tar.gz" 644',
      'file b/beta-1.2.3.tar.gz "beta-1.2.3.tar.gz" 644',
    ])
    finder = local_source_finder(tmp_dir)
    with self.assertRaises(RuntimeError) as context:
      finder.find_source('alpha', '1.2.3', 'linux')
    
if __name__ == '__main__':
  unit_test.main()
