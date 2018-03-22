
def rebuild_recipes(env):
  tests = [ 'all: fructose-test.c' ]
  configure_env = [
    'linux: CFLAGS="-I${REBUILD_REQUIREMENTS_INCLUDE_DIR} -std=gnu99" LDFLAGS=\"-L${REBUILD_REQUIREMENTS_LIB_DIR}\"',
  ]
  return env.args(
    properties = env.args(
      name = 'fructose',
      version = '3.4.5-6',
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
      'step_autoconf', {
        'tests': tests,
        'configure_env': configure_env,
      },
    ],
  )
