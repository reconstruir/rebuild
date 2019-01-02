#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.storage.storage_address import storage_address as SA
from rebuild.artifactory.artifactory_address import artifactory_address as AA

class test_storage_address(unit_test):

  def test_api_url(self):
    self.assertEqual( 'http://mycom.not/mycom/api',
                      AA.make_api_url(SA('http://mycom.not/mycom', 'repo', 'root', None, None)) )
    
  def test_search_aql_url(self):
    self.assertEqual( 'http://mycom.not/mycom/api/search/aql',
                      AA.make_search_aql_url(SA('http://mycom.not/mycom', 'repo', 'root', None, None)) )

if __name__ == '__main__':
  unit_test.main()
