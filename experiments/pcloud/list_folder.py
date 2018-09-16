import os, pprint

from rebuild.pcloud import pcloud

pc = pcloud('pcloud_rebuild@fateware.com',
            os.environ['PCLOUD_PASSWORD'])

x = pc.list_folder('/sources', recursive = True)
for i in x:
  print(str(i))
