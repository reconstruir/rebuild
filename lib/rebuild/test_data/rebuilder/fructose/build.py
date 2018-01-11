
def rebuild_recipes(env):

  tests = [
    'all: fructose1-test.c',
    'all: fructose2-test.c',
    'all: fructose-1and2-test.c',
  ]

  """
  caca_tests = '''
#source: fructose1-test.c
#requires: libfructose1
#system: all

source: fructose2-test.c
requires: libfructose2
system: all
'''
"""
  return env.args(
    properties = env.args(
      name = 'fructose',
      version = '3.4.5-6',
      category = 'lib',
    ),
    instructions = '''
libfructose1
  CFLAGS
    -I${REBUILD_PACKAGE_PREFIX}/include
  LDFLAGS
    -L${REBUILD_PACKAGE_PREFIX}/lib
  LIBS
    -lfructose1

libfructose2
  CFLAGS
    -I${REBUILD_PACKAGE_PREFIX}/include
    -I${REBUILD_PACKAGE_PREFIX}/include/caca
  LDFLAGS
    -L${REBUILD_PACKAGE_PREFIX}/lib
  LIBS
    -lfructose2

fructose
  requires
    libfructose2 libfructose1
    ''',
    requirements = [
    ],
    steps = [
      'step_autoconf', { 'tests': tests },
    ],
  )
