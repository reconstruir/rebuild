#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.recipe import recipe, recipe_parser
from rebuild.recipe.variable_manager import variable_manager
from bes.key_value import key_value_list as KVL

class recipe_parser_testing(object):

  @classmethod
  def text_add_indent(clazz, text, n):
    'Interpret text as lines and add n spaces to the head of each line.'
    indent = ' ' * n
    lines = text.split('\n')
    lines = [ '%s%s' % (indent, x) for x in lines ]
    return '\n'.join(lines)

  @classmethod
  def make_trivial_recipe(clazz, name, version, step_name, step_value):
    template = '''!rebuild.recipe!
package {name} {version}
  steps
    {step_name}
{step_value}
'''
    return template.format(name = name,
                           version = version,
                           step_name = step_name,
                           step_value = clazz.text_add_indent(step_value, 6))
    
  @classmethod
  def parse(clazz, text, filename = None, starting_line_number = None, variables = None):
    filename = filename or '<unknown>'
    starting_line_number = starting_line_number or 0
    vm = variable_manager()
    if variables:
      vm.add_variables(KVL.parse(variables))
    return recipe_parser(filename, text, starting_line_number = starting_line_number).parse(vm)

  @classmethod
  def parse_trivial_recipe(clazz, name, version, step_name, step_vaue,
                           filename = None, starting_line_number = None):
    recipe_text = clazz.make_trivial_recipe(name, version, step_name, step_vaue)
    recipe = clazz.parse(recipe_text, filename = filename, starting_line_number = starting_line_number)
    return recipe[0].steps[0].values[0].values
