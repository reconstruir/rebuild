import os, pprint

from rebuild.pcloud import pcloud

pc = pcloud('pcloud_rebuild@fateware.com',
            os.environ['PCLOUD_PASSWORD'])

#x = pc.checksum_file('/sources/z/zlib-1.2.8.tar.gz')
#print(pprint.pformat(x))
#raise SystemExit()

#f = pc.list_folder('/sources')
#print(pprint.pformat(f))

#FILENAME = '/home/ramiro/foo/sources/android/android-ndk-r17-darwin-x86_64.zip'
#DEST_DIR = '/sources/android'

LOCAL_FILENAME = '/home/ramiro/foo/sources/z/zlib-1.2.8.tar.gz'
CLOUD_FILENAME = '/sources/test1/z/caca/zlib-1.2.8.tar.gz'

#c = pc.checksum_file(file_path = CLOUD_FILENAME)
#print(pprint.pformat(c))

r = pc.upload_file(CLOUD_FILENAME, LOCAL_FILENAME)
print(pprint.pformat(r))
