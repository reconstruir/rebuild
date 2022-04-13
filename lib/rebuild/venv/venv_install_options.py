#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.property.cached_property import cached_property
from rebuild.package.package_install_options import package_install_options

class venv_install_options(namedtuple('venv_install_options', 'allow_downgrade, allow_same_version, wipe_first, dont_touch_scripts')):

  def __new__(clazz, allow_downgrade = False, allow_same_version = False, wipe_first = False, dont_touch_scripts = False):
    check.check_bool(allow_downgrade)
    check.check_bool(allow_same_version)
    check.check_bool(wipe_first)
    check.check_bool(dont_touch_scripts)
    return clazz.__bases__[0].__new__(clazz, allow_downgrade, allow_same_version, wipe_first, dont_touch_scripts)

  @cached_property
  def package_install_options(self):
    return package_install_options(allow_downgrade = self.allow_downgrade,
                                   allow_same_version = self.allow_same_version)
  
check.register_class(venv_install_options)
