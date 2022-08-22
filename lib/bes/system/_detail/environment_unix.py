#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
import os.path as path
import subprocess

from .environment_base import environment_base
from ..host import host

class environment_unix(environment_base):

  @classmethod
  #@abstractmethod
  def home_dir_env(clazz, home_dir):
    'Return a dict with the environment needed to set the home directory.'

    return {
      'HOME': home_dir,
    }

  _CLEAN_PATH = [
    '/usr/local/bin',
    '/usr/bin',
    '/bin',
    '/usr/sbin',
    '/sbin',
  ]
  _DECLARE_PATTERN = re.compile(r'^declare\s+--\s+PATH="(.+)"$')
  @classmethod
  #@abstractmethod
  def default_path(clazz):
    'The default system PATH.'
    if host.SYSTEM == host.LINUX and host.DISTRO == 'alpine':
      return [ '/usr/local/sbin', '/usr/local/bin', '/usr/sbin', '/usr/bin', '/sbin:/bin' ]
    cmd = [ 'env', '-i', 'bash', '--norc', '-c', 'declare -p PATH' ]
    try:
      rv = subprocess.run(cmd, capture_output = True, shell = False, check = True)
      f = clazz._DECLARE_PATTERN.findall(rv.stdout.decode())
      if not f:
        return clazz._CLEAN_PATH
      return f[0].split(path.pathsep)
    except Exception as ex:
      pass
    return clazz._CLEAN_PATH

  @classmethod
  #@abstractmethod
  def clean_path(clazz):
    'A clean system PATH with only the bare minimum needed to run shell commands.'
    return clazz._CLEAN_PATH

  @classmethod
  #@abstractmethod
  def clean_variables(clazz):
    'A list of variables clean system PATH with only the bare minimum needed to run shell commands.'
    return [
      'DISPLAY',
      'HOME',
      'LANG',
      'SHELL',
      'TEMP',
      'TERM',
      'TERM_PROGRAM',
      'TMOUT',
      'TMP',
      'TMPDIR',
      'USER',
      'XAUTHORITY',
      '__CF_USER_TEXT_ENCODING',
    ]
