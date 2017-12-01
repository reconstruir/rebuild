#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, unittest
from bes.common import check_type, dict_util
from test_steps import *
from rebuild.step import step, compound_step, step_description, step_manager

class test_step_manager(unittest.TestCase):

  def _make_step(self, name, fake_success = True, fake_message = ''):
    return sample_step_fake_success(name, fake_success, fake_message)

  def _add_test_step(self, sm, fake_name, fake_success = True):
    args = { 'fake_name': fake_name, 'fake_success': fake_success }
    description = step_description(sample_step_fake_success, args = args)
    return sm.add_step(description, {}, {})

  def test_add_step(self):
    sm = step_manager('sm')
    s = self._add_test_step(sm, 'one', True)
    self.assertEqual( { 'fake_name': 'one', 'fake_success': True }, s.args )

  def test_one_step(self):
    sm = step_manager('sm')

    self._add_test_step(sm, 'one', True)
    result = sm.execute({}, {}, {})
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )

  def test_success(self):
    sm = step_manager('sm')

    step_one_a = self._add_test_step(sm, 'one_a', True)
    step_one_b = self._add_test_step(sm, 'one_b', True)
    step_one_c = self._add_test_step(sm, 'one_c', True)

    step_two_a = self._add_test_step(sm, 'two_a', True)
    step_two_b = self._add_test_step(sm, 'two_b', True)
    step_two_c = self._add_test_step(sm, 'two_c', True)

    step_three_a = self._add_test_step(sm, 'three_a', True)
    step_three_b = self._add_test_step(sm, 'three_b', True)
    step_three_c = self._add_test_step(sm, 'three_c', True)

    result = sm.execute({}, {}, {})
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )

  def test_failed(self):
    sm = step_manager('sm')

    step_one_a = self._add_test_step(sm, 'one_a', True)
    step_one_b = self._add_test_step(sm, 'one_b', True)
    step_one_c = self._add_test_step(sm, 'one_c', True)

    step_two_a = self._add_test_step(sm, 'two_a', True)
    step_two_b = self._add_test_step(sm, 'two_b', False)
    step_two_c = self._add_test_step(sm, 'two_c', True)

    step_three_a = self._add_test_step(sm, 'three_a', True)
    step_three_b = self._add_test_step(sm, 'three_b', True)
    step_three_c = self._add_test_step(sm, 'three_c', True)

    result = sm.execute({}, {}, {})
    self.assertFalse( result.success )
    self.assertEqual( 'step two_b failed', result.message )
    self.assertEqual( step_two_b, result.failed_step )

  class SaveArgsStep(step):
    def __init__(self):
      super(test_step_manager.SaveArgsStep, self).__init__()
      self.saved_args = None

    def execute(self, script, env, args):
      self.saved_args = copy.deepcopy(args)
      return step_result(True, None)

  def _add_save_args_step(self, sm):
    description = step_description(self.SaveArgsStep)
    return sm.add_step(description, {}, {})

  def test_step_args(self):
    sm = step_manager('sm')

    bar_step = self._add_save_args_step(sm)

    step_args = { 'fruit': 'apple', 'num': 666 }

    bar_step.update_args(step_args)

    result = sm.execute({}, {}, {})
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )

    self.assertEqual( step_args, bar_step.saved_args )

  def test_global_args(self):
    sm = step_manager('sm')
    bar_step = self._add_save_args_step(sm)

    global_args = { 'food': 'steak', 'drink': 'wine' }

    result = sm.execute({}, global_args)
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )

    self.assertEqual( global_args, bar_step.saved_args )

  def test_step_and_global_args(self):
    sm = step_manager('sm')

    bar_step = self._add_save_args_step(sm)

    step_args = { 'fruit': 'apple', 'num': 666 }
    global_args = { 'food': 'steak', 'drink': 'wine' }

    final_args = dict_util.combine(step_args, global_args)

    bar_step.update_args(step_args)

    result = sm.execute({}, {}, global_args)
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )

    self.assertEqual( final_args, bar_step.saved_args )

  class test_multi_steps(compound_step):
    __steps__ = [ sample_step_save_args1, sample_step_save_args2, sample_step_save_args3 ]
    def __init__(self):
      super(test_step_manager.test_multi_steps, self).__init__()

  def test_multiple_step(self):
    self.maxDiff = None
    
    execute_args = { 'global_food': 'steak', 'global_drink': 'wine' }

    step1_args = { 'step1_fruit': 'apple', 'step1_num': 666 }
    step2_args = { 'step2_fruit': 'durian', 'step2_num': 667 }
    step3_args = { 'step3_fruit': 'mangosteen', 'step3_num': 668 }

    all_steps_args = dict_util.combine(step1_args, step2_args, step3_args)

    description_args1 = { 'desc1_wine': 'barolo', 'desc1_cheese': 'manchego' }
    description_args2 = { 'desc2_wine': 'barolo', 'desc2_cheese': 'manchego' }
    description_args3 = { 'desc3_wine': 'barolo', 'desc3_cheese': 'manchego' }

    description_args = dict_util.combine(description_args1, description_args2, description_args3)
    multi_step_description = step_description(self.test_multi_steps, args = description_args)

    sm = step_manager('sm')

    multi_step = sm.add_step(multi_step_description, {}, {})

    multi_step.update_args(all_steps_args)

    result = sm.execute({}, {}, execute_args)

    expected_saved_args = dict_util.combine(execute_args, all_steps_args, description_args)

    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )
    self.assertEqual( expected_saved_args, multi_step.steps[0].saved_args )
    self.assertEqual( expected_saved_args, multi_step.steps[1].saved_args )
    self.assertEqual( expected_saved_args, multi_step.steps[2].saved_args )

  def test_step_results(self):
    sm = step_manager('sm')
    script = {}
    env = {}
    s = sm.add_step(step_description(sample_step_fake_output1), script, env)
    expected_output = { 'foo': 6, 'bar': 'hi' }
    result = sm.execute(script, env, { 'fake_output': expected_output })
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )
    self.assertEqual( expected_output, result.output )

  class test_multi_step(compound_step):
    __steps__ = [ sample_step_fake_output1, sample_step_fake_output2, sample_step_fake_output3 ]
    def __init__(self):
      super(test_step_manager.test_multi_step, self).__init__()

  def test_multi_step_results(self):
    self.maxDiff = None

    sm = step_manager('sm')
    script = {}
    env = {}
    s = sm.add_step(step_description(self.test_multi_step), script, env)
    expected_output1 = { 'foo': 6, 'bar': 'hi' }
    expected_output2 = { 'fruit': 'kiwi', 'cheese': 'manchego' }
    expected_output3 = { 'wine': 'barolo', 'nut': 'almond' }
    execute_args = {
      'fake_output': expected_output1,
      'fake_output2': expected_output2,
      'fake_output3': expected_output3,
    }      
    expected_output = dict_util.combine(expected_output1, expected_output2, expected_output3)
    result = sm.execute(script, env, execute_args)
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )
    self.assertEqual( expected_output, result.output )

  class test_step_with_global_args(sample_step_save_args1):
    __step_global_args__ = {
      'global_arg1': 'foo',
      'global_arg2': 666,
    }
    def __init__(self):
      super(test_step_manager.test_step_with_global_args, self).__init__()

  def test_global_args(self):
    sm = step_manager('sm')
    s = sm.add_step(step_description(self.test_step_with_global_args), {}, {})
    result = sm.execute({}, {}, {})
    expected_saved_args = self.test_step_with_global_args.__step_global_args__
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )
    self.assertEqual( expected_saved_args, s.saved_args )

  class test_multi_step_with_global_args(compound_step):
    __steps__ = [ sample_step_save_args1, sample_step_save_args2, sample_step_save_args3 ]
    __step_global_args__ = {
      'global_arg3': 'hi',
      'global_arg4': 42,
    }
    def __init__(self):
      super(test_step_manager.test_multi_step_with_global_args, self).__init__()

  def test_compound_step_global_args(self):
    sm = step_manager('sm')
    s = sm.add_step(step_description(self.test_multi_step_with_global_args), {}, {})
    result = sm.execute({}, {}, {})
    expected_saved_args = self.test_multi_step_with_global_args.__step_global_args__
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )
    self.assertEqual( expected_saved_args, s.steps[0].saved_args )
    self.assertEqual( expected_saved_args, s.steps[1].saved_args )
    self.assertEqual( expected_saved_args, s.steps[2].saved_args )

  class test_multi_step_with_global_args_and_steps_with_global_args(compound_step):
    __steps__ = [ sample_step_save_args_with_global_args1, sample_step_save_args_with_global_args2, sample_step_save_args_with_global_args3 ]
    __step_global_args__ = {
      'global_arg1000': '1000',
      'global_arg1001': '1001',
    }
    def __init__(self):
      super(test_step_manager.test_multi_step_with_global_args_and_steps_with_global_args, self).__init__()

  def xtest_compound_step_global_args_with_steps_with_global_args(self):
    self.maxDiff = None
    sm = step_manager('sm')
    s = sm.add_step(step_description(self.test_multi_step_with_global_args_and_steps_with_global_args), {}, {})
    result = sm.execute({}, {}, {})
    expected_saved_args1 = dict_util.combine(sample_step_save_args_with_global_args1.__step_global_args__, self.test_multi_step_with_global_args_and_steps_with_global_args.__step_global_args__)
    expected_saved_args2 = dict_util.combine(sample_step_save_args_with_global_args2.__step_global_args__, self.test_multi_step_with_global_args_and_steps_with_global_args.__step_global_args__)
    expected_saved_args3 = dict_util.combine(sample_step_save_args_with_global_args3.__step_global_args__, self.test_multi_step_with_global_args_and_steps_with_global_args.__step_global_args__)
    self.assertTrue( result.success )
    self.assertEqual( None, result.message )
    self.assertEqual( None, result.failed_step )
    #self.assertEqual( expected_saved_args, s.saved_args )

    for k, v in sorted(expected_saved_args1.items()):
      print("EXPECTED: %s=%s" % (k, v))

    for k, v in sorted(step.steps[0].saved_args.items()):
      print("  ACTUAL: %s=%s" % (k, v))
    
    self.assertEqual( expected_saved_args1, step.steps[0].saved_args )
#    self.assertEqual( expected_saved_args2, step.steps[1].saved_args )
#    self.assertEqual( expected_saved_args3, step.steps[2].saved_args )

  def test_output_goes_to_next_step_args(self):
    sm = step_manager('sm')
    s1 = sm.add_step(step_description(step_with_output1), {}, {})
    s2 = sm.add_step(step_description(step_with_output2), {}, {})
    s3 = sm.add_step(step_description(step_with_output3), {}, {})
    s4 = sm.add_step(step_description(step_with_output4), {}, {})
    result = sm.execute({}, {}, {})
    self.assertTrue( result.success )
    self.assertEqual( {}, s1.saved_args )
    self.assertEqual( { 'foo': '5', 'bar': 6 }, s2.saved_args )
    self.assertEqual( { 'foo': '5', 'bar': 6, 'fruit': 'kiwi' }, s3.saved_args )
    self.assertEqual( { 'cheese': 'blue', 'foo': '5', 'bar': 6, 'fruit': 'kiwi' }, s4.saved_args )
    self.assertEqual( { 'drink': 'bourbon', 'cheese': 'blue', 'foo': '5', 'bar': 6, 'fruit': 'kiwi' }, result.output)

  class multi_step_with_steps_that_output(compound_step):
    __steps__ = [ step_with_output1, step_with_output2, step_with_output3, step_with_output4 ]
    def __init__(self):
      super(test_step_manager.multi_step_with_steps_that_output, self).__init__()
    
  def test_output_goes_to_next_step_args_multi_step(self):
    sm = step_manager('sm')
    s = sm.add_step(step_description(self.multi_step_with_steps_that_output), {}, {})
    result = sm.execute({}, {}, {})
    self.assertTrue( result.success )
    self.assertEqual( {}, s.steps[0].saved_args )
    self.assertEqual( { 'foo': '5', 'bar': 6 }, s.steps[1].saved_args )
    self.assertEqual( { 'foo': '5', 'bar': 6, 'fruit': 'kiwi' }, s.steps[2].saved_args )
    self.assertEqual( { 'cheese': 'blue', 'foo': '5', 'bar': 6, 'fruit': 'kiwi' }, s.steps[3].saved_args )
    
  @classmethod
  def _make_step_class(clazz, name,
                       result_code = 'step_result(True, None)',
                       parse_step_args_code = '{}'):
    code = '''
class %s(step):
  def __init__(self):
    super(%s, self).__init__()

    def execute(self, script, env, args):
      self.saved_args = copy.deepcopy(args)
      return %s

    @classmethod
    def parse_step_args(clazz, script, env, args):
      return %s
''' % (name, name, result_code, parse_step_args_code)
#    print(code)
    tmp_locals = {}
    exec(code, globals(), tmp_locals)
    assert name in tmp_locals
    result_class = tmp_locals[name]
    check_type.check_class(result_class, 'result_class')
    globals()[name] = result_class
    return result_class
    
if __name__ == '__main__':
  unittest.main()