#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import algorithm, check, type_checked_list
from bes.compat import StringIO
from rebuild.base import build_system
from bes.key_value import key_value, key_value_list
from bes.text import string_list

from .value import value_file
from .value import value_file_list
from .value import value_install_file

class masked_value_list(object):

  def __init__(self, values = None):
    self._values = []
    for value in values or []:
      check.check_masked_value(value)
      self._values.append(value)

  def __iter__(self):
    return iter(self._values)

  def __getitem__(self, i):
    return self._values[i]
  
  def __setitem__(self, i, value):
    check.check_masked_value(value)
    self._values[i] = value

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self._values == other._values
    elif isinstance(other, list):
      return self._values == other
    else:
      raise TypeError('other should be of masked_value_list type instead of %s' % (type(other)))
    
  def __str__(self):
    buf = StringIO()
    for value in self._values:
      buf.write(str(value))
      buf.write(';')
    return buf.getvalue()
    
  def append(self, value):
    check.check_masked_value(value)
    if self._values:
      expected_type = type(self._values[-1])
      actual_type = type(value)
      if expected_type != actual_type:
        raise TypeError('value should be of type %s instead of %s' % (expected_type, actual_type))
    self._values.append(value)

  def extend(self, values):
    for value in values:
      self.append(value)

  def __len__(self):
    return len(self._values)

  def resolve(self, system, arg_type):
    if not self._values:
      return []
    first_value = self._values[0].value
    values = self._resolve_values_by_mask(system)
    #print('FUCK: CACA: values=%s - %s' % (str(values), type(values)))
      
    if not values:
      return None
    
    if check.is_value_int(values[0]):
      return values[0].__class__.resolve(values, arg_type)
    elif check.is_value_string(values[0]):
      return values[0].__class__.resolve(values, arg_type)
    elif check.is_value_bool(values[0]):
      return values[0].__class__.resolve(values, arg_type)
    elif check.is_value_key_values(values[0]):
      return values[0].__class__.resolve(values, arg_type)
    elif check.is_string_list(values[0]):
      return self._resolve_string_list(values)
    elif check.is_value_file_list(values[0]):
      #return values[0][0].__class__.resolve(values, arg_type)
      #return values[0].__class__.resolve(values, arg_type)
      return self._resolve_typed_list(values, value_file_list)
    elif check.is_value_install_file(values[0]):
      return values[0].__class__.resolve(values, arg_type)
    elif check.is_value_hook(values[0]):
      return values[0].__class__.resolve(values, arg_type)
    elif check.is_value_file(values[0]):
      return values[0].__class__.resolve(values, arg_type)
    elif check.is_value_git_address(values[0]):
      return values[0].__class__.resolve(values, arg_type)
    elif check.is_value_source_tarball(values[0]):
      return values[0].__class__.resolve(values, arg_type)
    elif check.is_value_source_dir(values[0]):
      return values[0].__class__.resolve(values, arg_type)
    raise TypeError('unknown value type: %s - %s' % (str(values[0]), type(values[0])))

  def _resolve_values_by_mask(self, system):
    result = []
    for value in self._values:
      if value.mask_matches(system):
        result.append(value.value)
    return result

  def _resolve_typed_list(self, values, list_type):
    result = list_type()
    for value in values:
      assert isinstance(value, type_checked_list)
      result.extend(value)
    result.remove_dups()
    return result

  def _resolve_string_list(self, values):
    result = string_list()
    for value in values:
      check.check_string_list(value)
      result.extend(value)
    result.remove_dups()
    return result

check.register_class(masked_value_list, include_seq = False)
