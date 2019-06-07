#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .build_level import build_level
from .build_target import build_target

class build_target_cli(object):

  def __init__(self):
    pass

  def build_target_add_arguments(self, parser):
    default_build_target = build_target.make_host_build_target(level = build_level.RELEASE).build_path
    parser.add_argument('--build-target',
                        action = 'store',
                        type = str,
                        default = default_build_target,
                        help = 'Build target as a path. [ %s ]' % (default_build_target))

  def build_target_resolve(self, args):
    assert hasattr(args, 'build_target')
    check.check_string(args.build_target)
    args.build_target = build_target.parse_path(args.build_target)
    return args.build_target
