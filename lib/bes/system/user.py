#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, pwd

class user(object):

  USERNAME = pwd.getpwuid(os.getuid()).pw_name
