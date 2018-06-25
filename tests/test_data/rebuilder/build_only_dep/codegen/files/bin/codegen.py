#!/usr/bin/env python

import argparse, subprocess, os, sys

HEADER = '''
#ifndef {module_name}_h__
#define {module_name}_h__

extern int {env1}{env2}{module_name}_{function_name}();

#endif /* {module_name}_h__ */
'''

CODE = '''
#include "{module_name}.h"

int {env1}{env2}{module_name}_{function_name}()
{{
  return {return_value};
}}
'''

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument('module_name', action = 'store', help = 'module name.')
  ap.add_argument('function_name', action = 'store', help = 'function name.')
  ap.add_argument('return_value', action = 'store', help = 'return value.')
  ap.add_argument('--header', action = 'store_true', default = False, help = 'header instead of code. [ False ]')
  args = ap.parse_args()

  if args.header:
    template = HEADER
  else:
    template = CODE

  if not 'CODEGEN_ENV1' in os.environ:
    sys.stderr.write('codegen.py: env var CODEGEN_ENV1 not set.\n')
    sys.stderr.flush()
    raise SystemExit(1)
  
  if not 'CODEGEN_ENV2' in os.environ:
    sys.stderr.write('codegen.py: env var CODEGEN_ENV2 not set.\n')
    sys.stderr.flush()
    raise SystemExit(1)
  
  content = template.format(module_name = args.module_name,
                            function_name = args.function_name,
                            return_value = args.return_value,
                            env1 = os.environ['CODEGEN_ENV1'],
                            env2 = os.environ['CODEGEN_ENV2'])
  
  print(content)
  return 0
    
if __name__ == '__main__':
  raise SystemExit(main())

