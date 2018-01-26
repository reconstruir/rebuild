#!/bin/bash
automake -a && autoconf && ./configure && make distclean && ./configure && make && make distcheck
exit $?


