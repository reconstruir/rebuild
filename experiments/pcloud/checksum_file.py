import hashlib, os, pprint
from bes.fs import file_util

from rebuild.pcloud import pcloud

pc = pcloud('pcloud_rebuild@fateware.com',
            os.environ['PCLOUD_PASSWORD'])

#c = pc.checksum_file(file_path = '/sources/z/zlib-1.2.8.tar.gz')
c = pc.checksum_file(file_id = 8255973043)
print('remote checksum: %s' % (c))
print(' local checksum: %s' % (hashlib.sha1(file_util.read('/home/ramiro/foo/sources/z/zlib-1.2.8.tar.gz')).hexdigest()))
