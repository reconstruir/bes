#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, stat
from collections import namedtuple
from .file_find import file_find

class device_info(object):

  device = namedtuple('device', 'filename,type,major,minor')

  @classmethod
  def device_info(clazz, filename):
    'Return information about device or None if not a block or char device.'
    st = os.stat(filename)
    if stat.S_ISCHR(st.st_mode):
      dev_type = 'char'
    elif stat.S_ISBLK(st.st_mode):
      dev_type = 'block'
    else:
      return None
    return clazz.device(filename, dev_type, os.major(st.st_rdev), os.minor(st.st_rdev))

  @classmethod
  def scan_devices(clazz, d):
    'Recurisvely scan directory for devices and return device info for any that are char or block device.'
    files = file_find.find(d, relative = False, file_type = file_find.DEVICE)
    return [ clazz.device_info(f) for f in files ]
  
