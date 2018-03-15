#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import re
from collections import namedtuple
#from bes.common import check, node
#from bes.text import white_space

class package_metadata(namedtuple('package_metadata', 'name,version,system,distro,archs,category,level,requirements,build_tool_requirements,build_requirements,env_vars,pkg_config_name')):

  def __new__(clazz, name, version, system, distro, archs, category, level, requirements,
              build_tool_requirements, build_requirements, env_vars, pkg_config_name):
    if env_vars:
      check.check_masked_value_list(env_vars)
    return clazz.__bases__[0].__new__(name, version, system, distro, archs, category, level, requirements,
                                      build_tool_requirements, build_requirements, env_vars, pkg_config_name)

#  def __str__(self):
#    return self.to_string()

#  def to_string(self, depth = 0, indent = 2):
#    s = self._to_node().to_string(depth = depth, indent = indent).strip()
#    return white_space.shorten_multi_line_spaces(s)
