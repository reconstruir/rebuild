#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from bes.system.impl_import import impl_import
from bes.common.check import check

from bes.system.host import host
if host.SYSTEM == 'macos':
  from .native_package_manager_macos import native_package_manager_macos as native_package_manager
elif host.SYSTEM == 'linux':
  from .native_package_manager_linux import native_package_manager_linux as native_package_manager
else:
  raise RuntimeError('System not supported yet: "{}"'.format(host.SYSTEM))

check.register_class(native_package_manager,
                     name = 'native_package_manager',
                     include_seq = False)
#native_package_manager = impl_import.load(__name__, 'native_package_manager', globals())
