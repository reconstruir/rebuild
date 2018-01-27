AC_INIT([templatedepends], [1.2.3], [templatedepends-maintainer@fateware.com])
AM_INIT_AUTOMAKE([foreign])
AC_CONFIG_MACRO_DIRS([my_macros])
AC_PROG_CC
AC_PROG_RANLIB
AM_PROG_AR
echo FUCKFUCK
PKG_PROG_PKG_CONFIG([0.29.1])
#PKG_CHECK_MODULES([ZLIB], [$zlib_pkg], [have_zlib="yes (pkg-config)"], [:])
#PKG_CHECK_MODULES([OPENSSL], [openssl])
#echo "FUCKFUCK YOU"
#which pkg-config
#echo "HAVE_PKG_CONFIG:"  $HAVE_PKG_CONFIG
#AC_CHECK_PROG(HAVE_PKG_CONFIG, [ pkg-config ], [ yes ], [ no ])
#if test x"$HAVE_PKG_CONFIG" != x"yes" ; then
#  AC_MSG_ERROR([Please install pkg-config before installing.])
#fi
#m4_ifdef([AM_PROG_AR], [AM_PROG_AR])
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
