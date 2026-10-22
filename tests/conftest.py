#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# Tests never touch the real home directory.  This runs before any test
# module is imported, so a path computed at import time already sees the
# stand-in (bes/lib/bes/testing/unit_test_home.py).
from bes.testing import unit_test_home
unit_test_home.install()
