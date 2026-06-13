#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.system.host import host

from . import uv_installer_error

class _uv_installer_options_desc(bcli_options_desc):

  def _options_desc(self):
    return '''
install_dir    str  default=None
install_script str  default=None
version        str  default=None
verbose        bool default=False
dry_run        bool default=False
'''

  def _error_class(self):
    return uv_installer_error.uv_installer_error

class uv_installer_options(bcli_options):

  def __init__(self, **kwargs):
    super().__init__(_uv_installer_options_desc(), **kwargs)

  def resolve_install_dir(self):
    if self.install_dir:
      return self.install_dir
    if host.is_windows():
      user_profile = os.environ.get('USERPROFILE', path.expanduser('~'))
      return path.join(user_profile, '.local', 'bin')
    return path.join(path.expanduser('~'), '.local', 'bin')

uv_installer_options.register_check_class()
