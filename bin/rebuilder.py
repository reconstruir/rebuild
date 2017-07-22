#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import sys
sys.dont_write_bytecode = True
from rebuild.packager import rebuilder_cli

if __name__ == '__main__':
  rebuilder_cli.run()
