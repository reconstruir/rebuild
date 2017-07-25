#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.system import impl_loader

native_package_manager = impl_loader.load('native_package_manager', globals())
