#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

class shell_framework_defaults(object):

  ADDRESS = 'https://gitlab.com/rebuilder/bes_shell.git'
  FRAMEWORK_BASENAME = 'framework'
  REVISION_BASENAME = 'revision.txt'
  REVISION = 'latest'
  DEST_DIR = os.getcwd()
