#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common import check

class package_install_options(namedtuple('package_install_options', 'allow_downgrade, allow_same_version')):

  def __new__(clazz, allow_downgrade = False, allow_same_version = False):
    check.check_bool(allow_downgrade)
    check.check_bool(allow_same_version)
    return clazz.__bases__[0].__new__(clazz, allow_downgrade, allow_same_version)
  
check.register_class(package_install_options)
