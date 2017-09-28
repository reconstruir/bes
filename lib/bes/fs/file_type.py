#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import errno, os, stat
from bes.common import string_util

class file_type(object):

  BLOCK = 0x01
  CHAR = 0x02
  DIR = 0x04
  FILE = 0x08
  LINK = 0x10
  FIFO = 0x20
  SOCKET = 0x40
  DEVICE = BLOCK | CHAR
  ANY = BLOCK | CHAR | DIR | FILE | LINK | FIFO | SOCKET

  _NAME_TO_TYPE = {
    'block': BLOCK,
    'char': CHAR,
    'dir': DIR,
    'file': FILE,
    'link': LINK,
    'fifo': FIFO,
    'socket': SOCKET,
    'device': DEVICE,
    'any': ANY,
  }

  # These match those used by find -type X
  _SHORT_NAME_TO_TYPE = {
    'b': BLOCK,
    'c': CHAR,
    'd': DIR,
    'f': FILE,
    'l': LINK,
    'p': FIFO,
    's': SOCKET,
  }
  
  @classmethod
  def _want_file_type(clazz, file_type, mask):
    return (file_type & mask) != 0

  @classmethod
  def matches(clazz, filename, mask):
    try:
      st = os.lstat(filename)
    except OSError as ex:
      if ex.errno == errno.EBADF:
        # Some devices on macos result in bad access when trying to stat so ignore them
        return False
      else:
        raise
      
    match_block = clazz._want_file_type(mask, clazz.BLOCK) and stat.S_ISBLK(st.st_mode)
    match_char = clazz._want_file_type(mask, clazz.CHAR) and stat.S_ISCHR(st.st_mode)
    match_dir = clazz._want_file_type(mask, clazz.DIR) and stat.S_ISDIR(st.st_mode)
    match_fifo = clazz._want_file_type(mask, clazz.FIFO) and stat.S_ISFIFO(st.st_mode)
    match_file = clazz._want_file_type(mask, clazz.FILE) and stat.S_ISREG(st.st_mode)
    match_link = clazz._want_file_type(mask, clazz.LINK) and stat.S_ISLNK(st.st_mode)
    match_socket = clazz._want_file_type(mask, clazz.SOCKET) and stat.S_ISSOCK(st.st_mode)

    return match_block or match_char or match_dir or match_fifo or match_file or match_link or match_socket

  @classmethod
  def parse_file_type(clazz, s):
    if not string_util.is_string(s):
      return None
    t = clazz._NAME_TO_TYPE.get(s, None)
    if t:
      return t
    return clazz._SHORT_NAME_TO_TYPE.get(s, None)

  @classmethod
  def validate_file_type(clazz, s):
    t = clazz.parse_file_type(s)
    if t is None:
      raise ValueError('invalid file type: %s' % (s))
    return t
