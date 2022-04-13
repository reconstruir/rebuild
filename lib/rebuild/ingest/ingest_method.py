#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.system.log import log
from bes.common.node import node

from rebuild.recipe.value.masked_value_list import masked_value_list

from .ingest_method_descriptor_base import ingest_method_descriptor_base

class ingest_method(namedtuple('ingest_method', 'descriptor, values')):
  def __new__(clazz, descriptor, values):
    check.check_ingest_method_descriptor(descriptor)
    check.check_masked_value_list(values)
    return clazz.__bases__[0].__new__(clazz, descriptor, values)

  def to_node(self):
    node_name = 'method {}'.format(self.descriptor.method())
    method_node = node(node_name)
    for v in self.values:
      method_node.add_child(str(v))
    return method_node

  def resolve_values(self, system):
    return self.values.resolve(system, 'key_values')
  
  def download(self, values):
    return self.descriptor.download(values)
  
check.register_class(ingest_method, include_seq = False)
    
