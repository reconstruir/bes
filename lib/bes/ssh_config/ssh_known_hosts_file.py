#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.fs.file_util import file_util
from bes.property.cached_property import cached_property
from bes.text.text_line_parser import text_line_parser

from .ssh_config_error import ssh_config_error
from .ssh_known_host import ssh_known_host

class ssh_known_hosts_file(object):
  '''
  Class to deal with ~/.ssh/known_hosts format files described here:
  https://en.wikibooks.org/wiki/OpenSSH/Client_Configuration_Files#~/.ssh/known_hosts
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
      file_util.save(self._filename, content = '', codec = 'utf-8')
    return text_line_parser(file_util.read(self._filename, codec = 'utf-8'))
  
  def add_known_host(self, known_host):
    'Add a new known_host to the config file.'
    check.check_ssh_known_host(known_host)
    
    self._lines.append_line(str(known_host))
    self._save()

  def find_known_host(self, hostname):
    'Find a known_host by hostname.'
    check.check_string(hostname)

    if not path.exists(self._filename):
      return None
    
    for line in self._lines:
      if line.empty or line.is_comment:
        continue
      try:
        known_host = ssh_known_host.parse_text(line.text)
      except ssh_config_error as ex:
        msg = '{}:{}: {}'.format(self._filename, line.line_number, str(ex))
        raise ssh_config_error(msg)
      if hostname in known_host.hostnames:
        return known_host
    return None
    
  def _save(self):
    file_util.save(self._filename, content = str(self), mode = 0o0600, codec = 'utf-8')
