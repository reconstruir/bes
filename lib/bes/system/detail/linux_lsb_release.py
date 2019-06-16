#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import subprocess
from os import path
from collections import namedtuple

class linux_lsb_release(object):
  'Parse /etc/os-release'

  _parse_result = namedtuple('_parse_result', 'distro, version, family')
  @classmethod
  def parse_lsb_release(clazz, lsb_release):
    result = {}
    lines = lsb_release.strip().split('\n')
    for line in lines:
      parts = line.partition(':')
      if parts[1] != ':':
        raise RuntimeError('Invalid lsb_release entry: "%s"' % (line))
      result[parts[0].strip()] = parts[2].strip()
    return result

  @classmethod
  def has_lsb_release(clazz):
    'Return True if the lsb_release executable is found.'
    return clazz.lsb_release_exe() is not None
  
  @classmethod
  def lsb_release_exe(clazz):
    'Return the path to the lsb_release exe or None if not found.'
    try:
      return subprocess.check_output([ 'which', 'lsb_release' ]).strip()
    except Exception as ex:
      return None

  @classmethod
  def lsb_release_output(clazz):
    return subprocess.check_output([ 'lsb_release', '-v', '-a' ])
 
