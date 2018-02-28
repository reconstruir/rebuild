#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import script_unit_test
from bes.common import string_util
from bes.system import os_env

class test_rebuild_pkg_config(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/pkg_config/real_examples'
  __script__ = __file__, '../../bin/rebuild_pkg_config.py'

  ALL_MODULES = [
    'exiv2', 'freetype2', 'gdal', 'gio-2.0', 'gio-unix-2.0', 'glib-2.0',
    'gmodule-2.0', 'gmodule-export-2.0', 'gmodule-no-export-2.0', 'gobject-2.0',
    'gthread-2.0', 'IlmBase', 'ImageMagick', 'ImageMagick++', 'ImageMagick++-6.Q16',
    'ImageMagick-6.Q16', 'lept', 'libarchive', 'libavcodec', 'libavdevice',
    'libavfilter', 'libavformat', 'libavutil', 'libcrypto', 'libcurl', 'libffi',
    'libpng', 'libpng16', 'libssl', 'libswresample', 'libswscale', 'libtiff-4',
    'libwebp', 'libxml-2.0', 'Magick++', 'Magick++-6.Q16', 'MagickCore',
    'MagickCore-6.Q16', 'MagickWand', 'MagickWand-6.Q16', 'opencv', 'OpenEXR',
    'openssl', 'tesseract', 'Wand', 'Wand-6.Q16', 'zlib'
  ]

  @property
  def pc_path(self):
    return [ self.data_dir() ]

  @property
  def clean_env(self):
    return os_env.make_clean_env(update = { 'PKG_CONFIG_PATH': ':'.join(self.pc_path) },
                                 keep_keys = os_env.KEYS_THAT_ARE_PATHS)
  
  def test_list_all(self):
    self.maxDiff = None
    cmd = [
      '--list-all',
    ]
    rv = self.run_script(cmd, env = self.clean_env)
    self.assertEquals( 0, rv.exit_code )
    self.assertEquals( self.ALL_MODULES, self._parse_list_all_output(rv.stdout) )

  @classmethod
  def _parse_list_all_output(clazz, stdout):
    lines = stdout.strip().split('\n')
    return [ string_util.split_by_white_space(line, strip = True)[0] for line in lines ]

  def test_modversion(self):
    self.maxDiff = None
    cmd = [
      '--modversion',
    ] + self.ALL_MODULES
    rv = self.run_script(cmd, env = self.clean_env)
    expected_versions = [
      '0.24', '18.0.12', '2.0.0', '2.44.1', '2.44.1', '2.44.1', '2.44.1', '2.44.1',
      '2.44.1', '2.44.1', '2.44.1', '2.2.0', '6.9.2', '6.9.2', '6.9.2', '6.9.2',
      '1.72', '3.1.2', '56.41.100', '56.4.100', '5.16.101', '56.36.100', '54.27.100',
      '1.0.2d', '7.44.0', '3.2.1', '1.6.18', '1.6.18', '1.0.2d', '1.2.100', '3.1.101',
      '4.0.4', '0.4.3', '2.9.2', '6.9.2', '6.9.2', '6.9.2', '6.9.2', '6.9.2', '6.9.2',
      '3.0.0', '2.2.0', '1.0.2d', '3.02.02', '6.9.2', '6.9.2', '1.2.8',
    ]
    self.assertEquals( 0, rv.exit_code )
    self.assertEquals( expected_versions, rv.stdout.strip().split('\n') )

if __name__ == '__main__':
  script_unit_test.main()
