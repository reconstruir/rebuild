
def rebuild_recipes(env):
  tests = [ 'all: fiber-test.c' ]
  configure_env = [
    'linux: CFLAGS="-I${REBUILD_REQUIREMENTS_INCLUDE_DIR} -std=gnu99" LDFLAGS=\"-L${REBUILD_REQUIREMENTS_LIB_DIR}\"',
  ]
  return env.args(
    properties = env.args(
      name = 'fiber',
      version = '1.0.0-0',
      category = 'lib',
    ),
    instructions = '''
libfiber1
  CFLAGS
    -I${REBUILD_PACKAGE_PREFIX}/include
  LDFLAGS
    -L${REBUILD_PACKAGE_PREFIX}/lib
  LIBS
    -lfiber1

libfiber2
  CFLAGS
    -I${REBUILD_PACKAGE_PREFIX}/include
    -I${REBUILD_PACKAGE_PREFIX}/include/caca
  LDFLAGS
    -L${REBUILD_PACKAGE_PREFIX}/lib
  LIBS
    -lfiber2

fiber
  requires
    libfiber2 libfiber1
    ''',
    requirements = [
    ],
    steps = [
      'step_autoconf', {
#        'tests': tests,
        'configure_env': configure_env,
      },
    ],
  )
