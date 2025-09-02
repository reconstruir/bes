#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs
from os import path
import subprocess

import re

from collections import namedtuple

from ..system.check import check
from bes.common.string_util import string_util
from bes.fs.file_mime import file_mime
from bes.files.bf_path import bf_path
from bes.fs.filename_util import filename_util
from bes.system.env_override import env_override
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.execute import execute
#from bes.system.which import which

from bes.python.python_exe import python_exe as bes_python_exe
from bes.python.python_version import python_version as bes_python_version

from .pipenv_error import pipenv_error

class pipenv_exe(object):
  'Class to deal with the pipenv executable.'

  _log = logger('pipenv')
  
  _PIPENV_VERSION_PATTERN = r'^pipenv,\s+version\s+(.+)$'
  
  @classmethod
  def version(clazz, pipenv_exe):
    'Return the version info of a pipenv executable'
    check.check_string(pipenv_exe)

    cmd = [ pipenv_exe, '--version' ]
    rv = execute.execute(cmd)
    f = re.findall(clazz._PIPENV_VERSION_PATTERN, rv.stdout.strip())
    if not f:
      raise pipenv_error('not a valid pipenv version for {}: "{}"'.format(pipenv_exe, rv.stdout))
    if len(f) != 1:
      raise pipenv_error('not a valid pipenv version for {}: "{}"'.format(pipenv_exe, rv.stdout))
    version = f[0]
    return version
