import hashlib, os, os.path as path, requests, urlparse, pprint

API = 'https://api.pcloud.com'
USERNAME = 'pcloud_rebuild@fateware.com'
PASSWORD = os.environ['PCLOUD_PASSWORD']

url = urlparse.urljoin(API, 'getdigest') 
r = requests.get(url)
assert r.status_code == 200
payload = r.json()
digest = payload['digest']

username_digest = hashlib.sha1(USERNAME.lower()).hexdigest()
password_digest_input = PASSWORD + username_digest + digest
password_digest = hashlib.sha1(PASSWORD + username_digest + digest).hexdigest()

params = {
  'getauth': 1,
  'logout': 1,
  'username': USERNAME,
  'digest': digest,
  'passworddigest': password_digest,
}

url2 = urlparse.urljoin(API, 'userinfo') 
r2  = requests.get(url2, params = params)
assert r2.status_code == 200
payload2 = r2.json()
auth_token = payload2['auth']
#print(pprint.pformat(payload2))
print('auth_token: %s' % (auth_token))

url3 = urlparse.urljoin(API, 'listfolder') 
params3 = {
  'auth': auth_token,
  'path': '/caca',
}
r3  = requests.get(url3, params = params3)
assert r3.status_code == 200
payload3 = r3.json()
print(pprint.pformat(payload3))

filename = 'zlib-1.2.8.tar.gz'
fpath = path.join('/home/ramiro/foo/sources/z', filename)

#CACA: _upload() method=uploadfile; files={'zlib-1.2.8.tar.gz': <_io.BufferedReader name='/home/r#amiro/foo/sources/z/zlib-1.2.8.tar.gz'>}; kwargs={'path': '/caca', 'filename': 'zlib-1.2.8.tar.g#z'}


files4 = { filename: open(fpath, 'rb') }

url4 = urlparse.urljoin(API, 'uploadfile') 
params4 = {
  'auth': auth_token,
  'path': '/caca',
#  'data': fin.read(),
  'filename': filename,
}
r4  = requests.post(url4, data = params4, files = files4)
assert r4.status_code == 200
payload4 = r.json()
print(pprint.pformat(payload4))


'''
    @RequiredParameterCheck(('files', 'data'))
    def uploadfile(self, **kwargs):
        """ upload a file to pCloud

            1) You can specify a list of filenames to read
            files=['/home/pcloud/foo.txt', '/home/pcloud/bar.txt']

            2) you can specify binary data via the data parameter and
            need to specify the filename too
            data='Hello pCloud', filename='foo.txt'
        """
        if 'files' in kwargs:
            files = {}
            upload_files = kwargs.pop('files')
            for f in upload_files:
                filename = basename(f)
                files = {filename: open(f, 'rb')}
                kwargs['filename'] = filename
        else:  # 'data' in kwargs:
            files = {'f': (kwargs.pop('filename'), kwargs.pop('data'))}
        return self._upload('uploadfile', files, **kwargs)
'''
