#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib, os.path as path, requests, urlparse

class pcloud(object):

  API = 'https://api.pcloud.com'
  
  def __init__(self, email, password):
    digest = self._get_digest()
    password_digest = self._make_password_digest(digest, email, password)
    self._auth_token = self._get_auth_token(digest, email, password_digest)
    del email
    del password

  def list_folder(self, folder_path):
    url = self._make_api_url('listfolder')
    params = {
      'auth': self._auth_token,
      'path': folder_path,
    }
    response = requests.get(url, params = params)
    assert response.status_code == 200
    payload = response.json()
    return payload

  def list_folder(self, folder_path):
    url = self._make_api_url('listfolder')
    params = {
      'auth': self._auth_token,
      'path': folder_path,
    }
    response = requests.get(url, params = params)
    assert response.status_code == 200
    payload = response.json()
    return payload

  def checksum_file(self, file_path):
    url = self._make_api_url('checksumfile')
    params = {
      'auth': self._auth_token,
      'path': file_path,
    }
    response  = requests.get(url, params = params)
    assert response.status_code == 200
    payload = response.json()
    assert 'sha1' in payload
    return payload['sha1']
  
  @classmethod
  def _make_password_digest(clazz, digest, email, password):
    'Make a password digest.'
    email_digest = hashlib.sha1(email.lower()).hexdigest()
    password_digest_input = password + email_digest + digest
    return hashlib.sha1(password + email_digest + digest).hexdigest()

  @classmethod
  def _get_digest(clazz):
    'Get a digest from pcloud to use with subsequent api calls.'
    url = clazz._make_api_url('getdigest')
    response = requests.get(url)
    assert response.status_code == 200
    payload = response.json()
    assert 'digest' in payload
    return payload['digest']

  @classmethod
  def _get_auth_token(clazz, digest, email, password_digest):
    params = {
      'getauth': 1,
      'logout': 1,
      'digest': digest,
      'username': email,
      'passworddigest': password_digest,
    }
    url = clazz._make_api_url('userinfo')
    response  = requests.get(url, params = params)
    assert response.status_code == 200
    payload = response.json()
    assert 'auth' in payload
    return payload['auth']
  
  @classmethod
  def _make_api_url(clazz, method):
    return urlparse.urljoin(clazz.API, method)
