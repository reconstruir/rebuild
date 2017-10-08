#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test

import os.path as path
#from bes.fs import file_util, temp_file
from rebuild.pkg_config import caca_pkg_config

class test_caca_pkg_config(unit_test):

  __unit_test_data_dir__ = 'test_data/real_examples'
  
  def test_scan_dir(self):
    pc_files = caca_pkg_config.scan_dir(self.data_dir())
    self.assertEqual( [
      'IlmBase.pc', 'ImageMagick++-6.Q16.pc', 'ImageMagick++.pc', 'ImageMagick-6.Q16.pc', 'ImageMagick.pc', 
      'Magick++-6.Q16.pc', 'Magick++.pc', 'MagickCore-6.Q16.pc', 'MagickCore.pc', 'MagickWand-6.Q16.pc', 
      'MagickWand.pc', 'OpenEXR.pc', 'Wand-6.Q16.pc', 'Wand.pc', 'exiv2.pc', 'freetype2.pc', 'gdal.pc', 
      'gio-2.0.pc', 'gio-unix-2.0.pc', 'glib-2.0.pc', 'gmodule-2.0.pc', 'gmodule-export-2.0.pc', 
      'gmodule-no-export-2.0.pc', 'gobject-2.0.pc', 'gthread-2.0.pc', 'lept.pc', 'libarchive.pc', 
      'libavcodec.pc', 'libavdevice.pc', 'libavfilter.pc', 'libavformat.pc', 'libavutil.pc', 'libcrypto.pc', 
      'libcurl.pc', 'libffi.pc', 'libpng.pc', 'libpng16.pc', 'libssl.pc', 'libswresample.pc', 'libswscale.pc', 
      'libtiff-4.pc', 'libwebp.pc', 'libxml-2.0.pc', 'opencv.pc', 'openssl.pc', 'tesseract.pc', 'zlib.pc', 
    ], [ path.basename(f) for f in pc_files ] )

  def test_scan(self):
    pc_path = [ self.data_dir() ]
    rv = caca_pkg_config.scan(pc_path)
    self.assertEqual( {}, rv )

if __name__ == '__main__':
  unit_test.main()
