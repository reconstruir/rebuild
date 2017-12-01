#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

def rebuild_recipes(env):
  def _libsdl2(env):
    configure_env = [
      'all: CPPFLAGS="-I${REBUILD_REQUIREMENTS_DIR}/include ${REBUILD_COMPILE_CFLAGS}" LDFLAGS=-L${REBUILD_REQUIREMENTS_DIR}/lib CFLAGS="-I${REBUILD_REQUIREMENTS_DIR}/include ${REBUILD_COMPILE_CFLAGS}"',
    ]
    configure_flags = [
      'all: --enable-static --disable-shared',
      'linux: --with-pic',
    ]
    patches = [
      'all: reb-libsdl2-ar-flags.patch',
      'darwin: reb-libsdl2-macos-version.patch',
#      'linux: reb-libsdl2-x11-configure.patch',
    ]
    tests = [
      'desktop: reb-libsdl2-test.cpp',
    ]
    return env.args(
      enabled = '$system is MACOS',
      properties = env.args(
        name = 'libsdl2',
        version = '2.0.5',
        category = 'lib',
        pkg_config_name = 'sdl2',
        export_compilation_flags_requirements = [
          #          'all: ALL_DEPS',
#          'all: x11',
        ]
      ),
      requirements = [
#        'x11(linux) >= 1.6.4',
#        'xext(linux) >= 1.3.3',
#        'ice(linux) >= 1.0.9',
#        'sm(linux) >= 1.2.2',
#        'xrandr(linux) >= 1.5.1',
#        'libxxf86vm(linux) >= 1.1.4',
#        'xxf86dga(linux) >= 1.1.4',
#        'xscrnsaver(linux) >= 1.2.2',
#        'xinerama(linux) >= 1.1.3',
#        'xi(linux) >= 1.7.9',
#        'xcursor(linux) >= 1.1.14',
#        'xdamage(linux) >= 1.1.4',
#        'mesa(linux) >= 13.0.3',
      ],
      build_requirements = [
      ],
      steps = [
        'step_autoconf', {
          'configure_env': configure_env,
          'configure_flags': configure_flags,
          'tests': tests,
          'patches': patches,
#          'tarball_source_dir_override': 'SDL2-2.0.5',
        },
      ],
    )

  def _libsdl2_image(env):
    configure_env = [
      'all: LDFLAGS=${REBUILD_REQUIREMENTS_LDFLAGS} CFLAGS="${REBUILD_REQUIREMENTS_CFLAGS} ${REBUILD_COMPILE_CFLAGS}"',
      #'all: NEEDS_SSL_WITH_CRYPTO=1 NO_APPLE_COMMON_CRYPTO=1 NEEDS_LIBICONV=1 NO_GETTEXT=1 USE_LIBPCRE=1 APPLE_COMMON_CRYPTO=1',
    ]
    configure_flags = [
      'all: --with-sdl-prefix=$REBUILD_REQUIREMENTS_DIR --enable-jpg --disable-jpg-shared --disable-png-shared --disable-tif-shared --disable-webp-shared --enable-png --enable-tif --enable-webp --enable-static --disable-shared',
      'linux: --with-pic',
    ]
    patches = [
      'all: reb-libsdl2_image-no-programs.patch reb-libsdl2_image-pkgconfig.patch',
    ]
    tests = [
#      'desktop: reb-libsdl2_image-test.cpp',
    ]
    return env.args(
      enabled = '$system is MACOS',
      properties = env.args(
        name = 'libsdl2_image',
        version = '2.0.1',
        category = 'lib',
        pkg_config_name = 'SDL2_image',
        export_compilation_flags_requirements = [
          'all: ALL_DEPS',
        ],
      ),
      requirements = [
        'all: libsdl2 >= 2.0.5',
#        'all: libgif >= 5.1.1',
#        'all: libjpeg >= 9a',
#        'all: libpng >= 1.6.18',
#        'all: libtiff >= 4.0.4',
#        'all: libwebp >= 0.4.3',
      ],
      steps = [
        'step_autoconf', {
          'configure_env': configure_env,
          'configure_flags': configure_flags,
          'patches': patches,
          'tests': tests,
        },
      ],
    )
  def _libsdl2_mixer(env):
    configure_env = [
      'all: CFLAGS=${REBUILD_COMPILE_CFLAGS}',
    ]
    configure_flags = [
      'all: --with-sdl-prefix=$REBUILD_REQUIREMENTS_DIR --enable-static --disable-shared',
      'linux: --with-pic',
      'darwin: --disable-music-midi-native',
    ]
    return env.args(
      enabled = '$system is MACOS',
      properties = env.args(
        name = 'libsdl2_mixer',
        version = '2.0.1',
        category = 'lib',
      ),
      requirements = [
        'all: libsdl2 >= 2.0.5',
      ],
      steps = [
        'step_autoconf', {
          'configure_env': configure_env,
          'configure_flags': configure_flags,
        },
      ],
    )
  def _libsdl2_ttf(env):
    configure_env = [
      'all: CFLAGS=${REBUILD_COMPILE_CFLAGS}',
    ]
    configure_flags = [
      'all: --with-sdl-prefix=$REBUILD_REQUIREMENTS_DIR --with-freetype-prefix=$REBUILD_REQUIREMENTS_DIR --enable-static --disable-shared',
      'linux: --with-pic',
    ]
    patches = [
      'all: reb-libsdl2_ttf-no-programs.patch reb-libsdl2_ttf-pkgconfig.patch',
    ]
    tests = [
#      'desktop: reb-libsdl2_ttf-test.cpp',
    ]
    return env.args(
      enabled = '$system is MACOS',
      properties = env.args(
        name = 'libsdl2_ttf',
        version = '2.0.13',
        category = 'lib',
        pkg_config_name = 'SDL2_ttf',
      ),
      requirements = [
#        'all: freetype2 >= 2.6.2',
        'all: libsdl2 >= 2.0.5',
      ],
      steps = [
        'step_autoconf', {
          'configure_env': configure_env,
          'configure_flags': configure_flags,
          'patches': patches,
          'tests': tests,
        },
      ],
    )
  return [
    _libsdl2,
    _libsdl2_image,
    _libsdl2_mixer,
    _libsdl2_ttf,
  ]
