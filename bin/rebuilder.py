#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import sys
sys.dont_write_bytecode = True
from rebuild.packager import builder_cli

if __name__ == '__main__':
  builder_cli.run()
