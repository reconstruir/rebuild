#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_result

class step_setup_tarball_download(step):
  'Download a tarball.'

  def __init__(self):
    super(step_setup_tarball_download, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    tarball_address     string_list
    '''
    
  def execute(self, script, env, args):
    return step_result(True, None)

  def sources_keys(self):
    return [ 'downloaded_tarballs' ]

  @classmethod
  def parse_step_args(clazz, script, env, args):
    recipe = args.get('_CACA_REMOVE_ME_recipe', None)
    if recipe:
      values = recipe.resolve_values(env.config.build_target.system)
      tarball_address = values.get('tarball_address')
    else:
      tarball_address = args.get('tarball_address', None)

    if tarball_address:
      tarball_address_address = tarball_address[0]
      tarball_address_revision = tarball_address[1]
    else:
      tarball_address_address = None
      tarball_address_revision = None

    #print('FUCK: name=%s; tarball_address=%s;  address=%s;  revision=%s' % (script.descriptor.name, tarball_address, tarball_address_address, tarball_address_revision))
      
    result = {}
    #tarball_address, tarball_revision = args.get('tarball_address', ( None, None ))
    if tarball_address_address:
      dm = env.downloads_manager
      assert tarball_address_revision
      if not dm.has_tarball(tarball_address_address, tarball_address_revision):
        tarball_path = dm.tarball_path(tarball_address_address, tarball_address_revision)
        clazz.blurb('Downloading %s@%s to %s' % (tarball_address_address, tarball_address_revision, tarball_path))
      downloaded_path = dm.get_tarball(tarball_address_address, tarball_address_revision)
      result = { 'downloaded_tarballs': [ downloaded_path ] }
    return result
