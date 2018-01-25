#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import script_unit_test
from rebuild.pkg_config import caca_pkg_config

class test_rebuild_pkg_config(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/pkg_config/real_examples'
  __script__ = __file__, '../../bin/rebuild_pkg_config.py'

  def test_list_all(self):
    pc_path = [ self.data_dir() ]
    self.assertEquals( ['exiv2', 'freetype2', 'gdal', 'gio-2.0', 'gio-unix-2.0', 'glib-2.0', 'gmodule-2.0', 'gmodule-export-2.0', 'gmodule-no-export-2.0', 'gobject-2.0', 'gthread-2.0', 'IlmBase', 'ImageMagick', 'ImageMagick++', 'ImageMagick++-6.Q16', 'ImageMagick-6.Q16', 'lept', 'libarchive', 'libavcodec', 'libavdevice', 'libavfilter', 'libavformat', 'libavutil', 'libcrypto', 'libcurl', 'libffi', 'libpng', 'libpng16', 'libssl', 'libswresample', 'libswscale', 'libtiff-4', 'libwebp', 'libxml-2.0', 'Magick++', 'Magick++-6.Q16', 'MagickCore', 'MagickCore-6.Q16', 'MagickWand', 'MagickWand-6.Q16', 'opencv', 'OpenEXR', 'openssl', 'tesseract', 'Wand', 'Wand-6.Q16', 'zlib'],
                       [ mod.name for mod in caca_pkg_config.list_all(pc_path) ] )

if __name__ == '__main__':
  script_unit_test.main()
