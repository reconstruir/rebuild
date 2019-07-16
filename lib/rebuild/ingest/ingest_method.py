#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.system.log import log
from bes.common.node import node

from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.recipe_util import recipe_util

class ingest_method(namedtuple('ingest_method', 'method, values')):
  def __new__(clazz, method, values):
    check.check_string(method)
    check.check_masked_value_list(values)
    return clazz.__bases__[0].__new__(clazz, method , values)

  def to_node(self):
    node_name = 'method {}'.format(self.method)
    method_node = node(node_name)
    for v in self.values:
      method_node.add_child(str(v))
    return method_node
  
check.register_class(ingest_method, include_seq = False)
    
