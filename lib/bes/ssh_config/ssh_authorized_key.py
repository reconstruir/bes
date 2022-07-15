#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from bes.common.string_util import string_util
from bes.compat.StringIO import StringIO
from bes.fs.file_util import file_util

from .ssh_config_error import ssh_config_error

class ssh_authorized_key(namedtuple('ssh_authorized_key', 'key_type, key, annotation')):

  def __new__(clazz, key_type, key, annotation):
    check.check_string(key_type)
    check.check_string(key)
    check.check_string(annotation, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, key_type, key, annotation)

  def __str__(self):
    buf = StringIO()
    buf.write(self.key_type)
    buf.write(' ')
    buf.write(self.key)
    if self.annotation:
      buf.write(' ')
      buf.write(self.annotation)
    return buf.getvalue()
  
  @classmethod
  def parse_text(clazz, text):
    parts = string_util.split_by_white_space(text, strip = True)
    if len(parts) < 3:
      raise ssh_config_error('Invalid authorized_key entry (should have at least 3 parts): "{}"'.format(text))
    key_type = parts.pop(0)
    key = parts.pop(0)
    i = text.find(key) + len(key)
    annotation = text[i:].strip()
    return ssh_authorized_key(key_type, key, annotation)

  @classmethod
  def parse_file(clazz, filename):
    return clazz.parse_text(file_util.read(filename, codec = 'utf-8'))

check.register_class(ssh_authorized_key)
