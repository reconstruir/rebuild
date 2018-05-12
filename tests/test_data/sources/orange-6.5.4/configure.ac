AC_INIT([orange], [6.5.4], [orange-maintainer@fateware.com])
AM_INIT_AUTOMAKE([foreign])
AC_CONFIG_MACRO_DIRS([my_macros])
AC_PROG_CC
AC_PROG_RANLIB
AM_PROG_AR
PKG_PROG_PKG_CONFIG([0.29.1])
orange1_REQUIRES="template"
AC_SUBST(template1_REQUIRES)
template1_LIBS="-ltemplate1"
AC_SUBST(template1_LIBS)
template1_LIBS_PRIVATE=""
AC_SUBST(template1_LIBS_PRIVATE)
template1_CFLAGS="-DTEMPLATE1"
AC_SUBST(template1_CFLAGS)
template2_REQUIRES="template"
AC_SUBST(template2_REQUIRES)
template2_LIBS="-ltemplate2"
AC_SUBST(template2_LIBS)
template2_LIBS_PRIVATE=""
AC_SUBST(template2_LIBS_PRIVATE)
template2_CFLAGS="-DTEMPLATE2"
AC_SUBST(template2_CFLAGS)
#@REB_17@
#@REB_18@
#@REB_19@
#@REB_20@
#PKG_CHECK_MODULES([ZLIB], [$zlib_pkg], [have_zlib="yes (pkg-config)"], [:])
#PKG_CHECK_MODULES([ZLIB], [zlib]) #, [have_zlib="yes (pkg-config)"], [:])
#PKG_CHECK_MODULES([OPENSSL], [openssl])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([
 Makefile
 libs/Makefile
 libs/orange1/Makefile
 libs/orange2/Makefile
 liborange1.pc
 liborange2.pc
 my_macros/Makefile
 programs/Makefile
 programs/orange_program1/Makefile
 programs/orange_program2/Makefile
 orange.pc
])
AC_OUTPUT
