AC_INIT([templatedepends], [1.2.3], [templatedepends-maintainer@fateware.com])
AM_INIT_AUTOMAKE([foreign])
AC_CONFIG_MACRO_DIRS([my_macros])
AC_PROG_CC
AC_PROG_RANLIB
AM_PROG_AR
PKG_PROG_PKG_CONFIG([0.29.1])
#@REB_01@
#@REB_02@
#@REB_03@
#@REB_04@
#@REB_05@
#@REB_06@
#@REB_07@
#@REB_08@
#@REB_09@
#@REB_10@
#@REB_11@
#@REB_12@
#@REB_13@
#@REB_14@
#@REB_15@
#@REB_16@
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
