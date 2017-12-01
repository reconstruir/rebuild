
def rebuild_recipes(env):
  tests = [ 'all: fiber-test.c' ]
  return env.args(
    properties = env.args(
      name = 'fiber',
      version = '1.0.0-0',
      category = 'lib',
    ),
    instructions = '''
name: libfiber1
CFLAGS: -I${REBUILD_PACKAGE_PREFIX}/include
LDFLAGS: -L${REBUILD_PACKAGE_PREFIX}/lib
LIBS: -lfiber1

name: libfiber2
CFLAGS: -I${REBUILD_PACKAGE_PREFIX}/include
        -I${REBUILD_PACKAGE_PREFIX}/include/caca
LDFLAGS: -L${REBUILD_PACKAGE_PREFIX}/lib
LIBS: -lfiber2

name: fiber
requires: libfiber2 libfiber1
    ''',
    requirements = [
    ],
    steps = [
      'step_autoconf', { 'tests': tests },
    ],
  )
