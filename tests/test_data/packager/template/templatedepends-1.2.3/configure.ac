AC_INIT([templatedepends], [1.2.3], [templatedepends-maintainer@fateware.com])
AM_INIT_AUTOMAKE([foreign])
AC_CONFIG_MACRO_DIRS([my_macros])
AC_PROG_CC
AC_PROG_RANLIB
AM_PROG_AR
PKG_PROG_PKG_CONFIG([0.29.1])
#PKG_CHECK_MODULES([ZLIB], [$zlib_pkg], [have_zlib="yes (pkg-config)"], [:])
#PKG_CHECK_MODULES([ZLIB], [zlib]) #, [have_zlib="yes (pkg-config)"], [:])
#PKG_CHECK_MODULES([OPENSSL], [openssl])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([
 Makefile
 libs/Makefile
 libs/templatedepends1/Makefile
 libs/templatedepends2/Makefile
 libtemplatedepends1.pc
 libtemplatedepends2.pc
 my_macros/Makefile
 programs/Makefile
 programs/templatedepends_program1/Makefile
 programs/templatedepends_program2/Makefile
 templatedepends.pc
])
AC_OUTPUT
