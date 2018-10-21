#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .build_arch import build_arch
from .build_level import build_level
from .build_system import build_system
from .build_target import build_target

class build_target_cli(object):

  def __init__(self):
    pass

  def build_target_add_arguments(self, parser):
    archs = ','.join(build_arch.DEFAULT_HOST_ARCHS)
    build_levels = ','.join(build_level.LEVELS)
    systems = ','.join(build_system.SYSTEMS)
    default_system = build_system.HOST
    default_level = build_level.RELEASE
    default_arch = build_arch.HOST_ARCH
    default_distro = build_system.HOST_DISTRO
    parser.add_argument('-s', '--system',
                        action = 'store',
                        type = str,
                        default = default_system,
                        help = 'build_system.  One of (%s) [ %s ]' % (systems, default_system))
    parser.add_argument('-a', '--arch',
                        action = 'store',
                        type = str,
                        default = default_arch,
                        help = 'Architecture(s) to build for.  One or more of (%s) [ %s ]' % (archs, default_arch))
    parser.add_argument('-l', '--level',
                        action = 'store',
                        type = str,
                        default = default_level,
                        help = 'Build level.  One of (%s) [ %s ]' % (build_levels, default_level))
    parser.add_argument('-d', '--distro',
                        action = 'store',
                        type = str,
                        default = default_distro,
                        help = 'Distro. [ %s ]' % (default_distro))

  def build_target_resolve(self, args):
    args.system = build_system.parse_system(args.system)
    args.level = build_level.parse_level(args.level)
    args.arch = build_arch.parse_arch(args.arch, args.system, args.distro)
    args.build_target = build_target(args.system, args.distro, build_system.HOST_VERSION, args.arch, args.level)
    return args.build_target
