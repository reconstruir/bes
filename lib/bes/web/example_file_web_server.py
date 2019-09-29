#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.web.web_server_app import web_server_app
from bes.web.file_web_server import file_web_server

if __name__ == '__main__':
  raise SystemExit(web_server_app(file_web_server).main())
  
