#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .build_arch import build_arch
from .build_level import build_level
from .build_system import build_system
from .build_target import build_target

class build_target_cli(object):

  SYSTEM_CHOICES = [ 'default' ] + build_system.SYSTEMS
  SYSTEM_DEFAULT = build_system.DEFAULT
  ARCH_CHOICES = [ 'default' ] + build_arch.KNOWN_ARCHS
  LEVEL_CHOICES = [ 'default' ] + build_level.LEVELS

  BUILD_LEVELS_BLURB = ','.join(build_level.LEVELS)
  ARCHS_BLURB = ','.join(build_arch.DEFAULT_HOST_ARCHS)
  DEFAULT_ARCHS_BLURB = ','.join(build_arch.DEFAULT_HOST_ARCHS)
  SYSTEM_CHOICES_BLURB = ','.join(SYSTEM_CHOICES)
  
  def __init__(self):
    pass

  def build_target_add_arguments(self, parser):
    parser.add_argument('-s', '--system',
                        action = 'store',
                        type = str,
                        default = self.SYSTEM_DEFAULT,
                        help = 'system to build for.  One of (%s) [ %s ]' % (self.SYSTEM_CHOICES_BLURB, self.SYSTEM_DEFAULT))
    parser.add_argument('-a', '--arch',
                        action = 'append',
                        type = str, 
                        choices = self.ARCH_CHOICES,
                        default = [],
                        help = 'Architectures to build for.  One of (%s) [ %s ]' % (self.ARCHS_BLURB, self.DEFAULT_ARCHS_BLURB))
    parser.add_argument('-l', '--level',
                        action = 'store',
                        type = str,
                        default = build_level.DEFAULT_LEVEL,
                        choices = self.LEVEL_CHOICES,
                        help = 'Build level.  One of (%s) [ %s ]' % (self.BUILD_LEVELS_BLURB, build_level.DEFAULT_LEVEL))
    
  def build_target_resolve(self, args):
    print('system: %s' % (args.system))
    print('  arch: %s' % (args.arch))
    print(' level: %s' % (args.level))
    return None
