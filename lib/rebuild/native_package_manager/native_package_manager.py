#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.system.impl_import import impl_import

from bes.system.host import host
if host.SYSTEM == 'macos':
  from .native_package_manager_macos import native_package_manager_macos as native_package_manager
elif host.SYSTEM == 'linux':
  from .native_package_manager_linux import native_package_manager_linux as native_package_manager

#native_package_manager = impl_import.load(__name__, 'native_package_manager', globals())
