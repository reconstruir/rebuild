#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.web.web_server_app import web_server_app
from mock_artifactory_server import mock_artifactory_server

if __name__ == '__main__':
  raise SystemExit(web_server_app(mock_artifactory_server).main())
