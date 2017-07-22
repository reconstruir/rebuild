
def rebuild_recipes(env):
  tests = [ 'all: fructose-test.c' ]
  return env.args(
    properties = env.args(
      name = 'fructose',
      version = '3.4.5-6',
      category = 'lib',
    ),
    instructions = '''
name: libfructose1
CFLAGS: -I${REBUILD_PACKAGE_PREFIX}/include
LDFLAGS: -L${REBUILD_PACKAGE_PREFIX}/lib
LIBS: -lfructose1

name: libfructose2
CFLAGS: -I${REBUILD_PACKAGE_PREFIX}/include
        -I${REBUILD_PACKAGE_PREFIX}/include/caca
LDFLAGS: -L${REBUILD_PACKAGE_PREFIX}/lib
LIBS: -lfructose2

name: fructose
requires: libfructose2 libfructose1
    ''',
    requirements = [
    ],
    steps = [
      step_autoconf, { 'tests': tests },
    ],
  )
