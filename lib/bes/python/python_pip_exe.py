#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs
import os
import re
import subprocess

from collections import namedtuple

from bes.common.check import check
from bes.system.env_override import env_override
from bes.system.log import logger

from .python_error import python_error

class python_pip_exe(object):
  'Class to call pip --version and parse the output.'

  _log = logger('python')
  
  _PIP_VERSION_PATTERN = r'^pip\s+([\d\.]+)\s+from\s+(.+)\s+\(python\s+(\d+\.\d+)\)$'
  
  _pip_version_info = namedtuple('_pip_version_info', 'version, where, python_version')
  @classmethod
  def version_info(clazz, pip_exe, pythonpath = None):
    'Return the version info of a pip executable'
    check.check_string(pip_exe)
    check.check_string_seq(pythonpath, allow_none = True)

    pythonpath = pythonpath or []
    
    cmd = [ pip_exe, '--version' ]
    env_PYTHONPATH = os.pathsep.join(pythonpath)
    with env_override(env = { 'PYTHONPATH': env_PYTHONPATH }) as env:
      clazz._log.log_d('pip_exe={} PYTHONPATH={}'.format(pip_exe, env_PYTHONPATH))
      try:
        output_bytes = subprocess.check_output(cmd, stderr = subprocess.STDOUT)
        output = codecs.decode(output_bytes, 'utf-8').strip()
      except subprocess.CalledProcessError as ex:
        msg = 'Failed to run: "{}" - {}'.format(' '.join(cmd), ex.output)
        clazz._log.log_w(msg)
        raise ython_error(msg, status_code = ex.returncode)
    f = re.findall(clazz._PIP_VERSION_PATTERN, output)
    if not f:
      raise python_error('not a valid pip version for {}: "{}"'.format(pip_exe, output))
    if len(f[0]) != 3:
      raise python_error('not a valid pip version for {}: "{}"'.format(pip_exe, output))
    version = f[0][0]
    where = f[0][1]
    python_version = f[0][2]
    return clazz._pip_version_info(version, where, python_version)
