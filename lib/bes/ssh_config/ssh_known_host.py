#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from bes.common.string_util import string_util
from bes.compat.StringIO import StringIO

from .ssh_config_error import ssh_config_error

class ssh_known_host(namedtuple('ssh_known_host', 'hostnames, key_type, key, comment')):

  def __new__(clazz, hostnames, key_type, key, comment = None):
    check.check_string_seq(hostnames)
    check.check_string(key_type)
    check.check_string(key)
    check.check_string(comment, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, hostnames, key_type, key, comment)

  def __str__(self):
    buf = StringIO()
    for i, hostname in enumerate(self.hostnames):
      if i != 0:
        buf.write(',')
      buf.write(hostname)
    buf.write(' ')
    buf.write(self.key_type)
    buf.write(' ')
    buf.write(self.key)
    if self.comment:
      buf.write(' # ')
      buf.write(self.comment)
    return buf.getvalue()
  
  @classmethod
  def parse_text(clazz, text):
    parts = string_util.split_by_white_space(text, strip = True)
    if len(parts) < 3:
      raise ssh_config_error('Invalid known_hosts entry (should have at least 3 parts): "{}"'.format(text))
    hostnames = parts.pop(0).split(',')
    key_type = parts.pop(0)
    key = parts.pop(0)
    i = text.find(key) + len(key)
    comment = text[i:].strip() or None
    if comment:
      if not comment.startswith('#'):
        raise ssh_config_error('Invalid known_hosts entry (extraneous text instead of comment): "{}"'.format(text))
      comment = comment[1:].strip()
    return ssh_known_host(hostnames, key_type, key, comment = comment)

check.register_class(ssh_known_host)
