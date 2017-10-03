#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.system import impl_import

native_package_manager = impl_import.load(__name__, 'native_package_manager', globals())
