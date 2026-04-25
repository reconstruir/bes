#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from bes.files.bf_file_ops import bf_file_ops
from bes.property.cached_property import cached_property
from bes.text.text_line_parser import text_line_parser

from .ssh_config_error import ssh_config_error
from .ssh_authorized_key import ssh_authorized_key

class ssh_authorized_keys_file(object):
  '''
  Class to deal with ~/.ssh/authorized_keys format files described here:
  https://en.wikibooks.org/wiki/OpenSSH/Client_Configuration_Files#~/.ssh/authorized_keys
  '''

  def __init__(self, filename):
    self._filename = filename
    if path.exists(self._filename):
      if not path.isfile(self._filename):
        raise ssh_config_error('Not a file: ): "{}"'.format(self._filename))

  def __str__(self):
    return str(self._lines)

  @cached_property
  def _lines(self):
    if not path.exists(self._filename):
      bf_file_ops.save(self._filename, content = '', encoding = 'utf-8')
    return text_line_parser(bf_file_ops.read(self._filename, encoding = 'utf-8'))
  
  def add_authorized_key(self, authorized_key):
    'Add a new authorized_key to the config file.'
    check.check_ssh_authorized_key(authorized_key)
    
    self._lines.append_line(str(authorized_key))
    self._save()

  def _save(self):
    bf_file_ops.save(self._filename, content = str(self), perm = 0o0600, encoding = 'utf-8')
