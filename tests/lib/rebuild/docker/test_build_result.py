#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
#from rebuild.project.project_file import project_file as PF
#from rebuild.recipe.value import masked_value, masked_value_list, value_origin, value_key_values, value_string_list
#from bes.key_value import key_value_list
#from bes.text import string_list
#from bes.fs import temp_file

from rebuild.docker.build_result import build_result

class test_build_result(unit_test):

  def test_parse_build_result(self):
    text = '''\
Sending build context to Docker daemon  4.096kB
Step 1/3 : FROM fedora:29
 ---> d7372e6c93c6
Step 2/3 : WORKDIR /root
 ---> Using cache
 ---> 4704f6dddffc
Step 3/3 : CMD /bin/true
 ---> Using cache
 ---> 1f1f4e88138b
Successfully built abcdef123456
Successfully tagged tag:latest
'''
    b = build_result.parse_build_result(text)
    self.assertEqual( 'abcdef123456', b.image_id )
    self.assertEqual( 'tag:latest', b.tag )

    text = '''\
Sending build context to Docker daemon  4.096kB

Step 1/3 : FROM fedora:29
 ---> d7372e6c93c6
Step 2/3 : WORKDIR /root
 ---> Using cache
 ---> 4704f6dddffc
Step 3/3 : CMD /bin/true
 ---> Using cache
 ---> 1f1f4e88138b
Successfully built 1f1f4e88138b
'''
    self.assertEqual( ( '1f1f4e88138b', None ), build_result.parse_build_result(text) )
    
if __name__ == '__main__':
  unit_test.main()
