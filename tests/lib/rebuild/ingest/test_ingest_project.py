#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.ingest.ingest_project import ingest_project
from bes.fs.file_util import file_util

class test_ingest_project(unit_test):

  def test_files(self):
    tmp_dir = self._make_temp_content()
    p = ingest_project(tmp_dir)
    self.assertEqual( [
      'cheese/hard/cheddar.reingest',
      'cheese/soft/brie.reingest',
      'fruit/kiwi.reingest',
      'fruit/orange.reingest',
    ], p.files )

  def test_load(self):
    tmp_dir = self._make_temp_content()
    p = ingest_project(tmp_dir)
    p.load()
    
  def _make_temp_content(self):
    content_kiwi = '''!rebuild.ingest.v1!
entry libkiwi 2.3.4

  data
    all: checksum 2.3.4 0123456789001234567890012345678900123456789001234567890012345678
    all: checksum 2.3.5 abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd

  variables
    all: _home_url=http://example.com/kiwi
    all: _upstream_name=kiwi
    all: _upstream_filename=${_upstream_name}-${VERSION}.tar.gz
    all: _filename=${NAME}-${VERSION}.tar.gz
    all: _ingested_filename=lib/${_filename}

  method http
    all: url=http://www.examples.com/kiwi.zip
    all: checksum=chk
    all: ingested_filename=kiwi.zip
'''

    content_orange = '''!rebuild.ingest.v1!
entry liborange 5.6.7

  data
    all: checksum 5.6.7 0123456789001234567890012345678900123456789001234567890012345678
    all: checksum 5.6.8 abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd

  variables
    all: _home_url=http://example.com/orange
    all: _upstream_name=orange
    all: _upstream_filename=${_upstream_name}-${VERSION}.tar.gz
    all: _filename=${NAME}-${VERSION}.tar.gz
    all: _ingested_filename=lib/${_filename}

  method http
    all: url=http://www.examples.com/orange.zip
    all: checksum=chk
    all: ingested_filename=orange.zip
'''
    
    content_cheddar = '''!rebuild.ingest.v1!
entry libcheddar 5.6.7

  data
    all: checksum 5.6.7 0123456789001234567890012345678900123456789001234567890012345678
    all: checksum 5.6.8 abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd

  variables
    all: _home_url=http://example.com/lemon
    all: _upstream_name=lemon
    all: _upstream_filename=${_upstream_name}-${VERSION}.tar.gz
    all: _filename=${NAME}-${VERSION}.tar.gz
    all: _ingested_filename=lib/${_filename}

  method http
    all: url=http://www.examples.com/lemon.zip
    all: checksum=chk
    all: ingested_filename=lemon.zip
'''

    content_brie = '''!rebuild.ingest.v1!
entry libbrie 6.6.6

  data
    all: checksum 6.6.6 0123456789001234567890012345678900123456789001234567890012345678
    all: checksum 6.6.7 abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd

  variables
    all: _home_url=http://example.com/lemon
    all: _upstream_name=lemon
    all: _upstream_filename=${_upstream_name}-${VERSION}.tar.gz
    all: _filename=${NAME}-${VERSION}.tar.gz
    all: _ingested_filename=lib/${_filename}

  method http
    all: url=http://www.examples.com/lemon.zip
    all: checksum=chk
    all: ingested_filename=lemon.zip
'''
    
    tmp_dir = self.make_temp_dir()
    file_util.save(path.join(tmp_dir, 'fruit', 'kiwi.reingest'), content = content_kiwi)
    file_util.save(path.join(tmp_dir, 'fruit', 'orange.reingest'), content = content_orange)
    file_util.save(path.join(tmp_dir, 'cheese', 'hard', 'cheddar.reingest'), content = content_cheddar)
    file_util.save(path.join(tmp_dir, 'cheese', 'soft', 'brie.reingest'), content = content_brie)
    return tmp_dir
    
if __name__ == '__main__':
  unit_test.main()
