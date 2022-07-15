#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from bes.common.string_util import string_util
from bes.config.simple_config import simple_config
from bes.config.simple_config_entry import simple_config_entry
from bes.config.simple_config_error import simple_config_error
from bes.config.simple_config_origin import simple_config_origin
from bes.fs.file_util import file_util
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.property.cached_property import cached_property

from .ssh_config_error import ssh_config_error

class ssh_config_file(object):
  '''
  Class to deal with ~/.ssh/known_hosts format files described here:
  https://en.wikibooks.org/wiki/OpenSSH/Client_Configuration_Files#~/.ssh/config
  '''

  def __init__(self, filename):
    self._filename = filename
    if path.exists(self._filename):
      if not path.isfile(self._filename):
        raise simple_config_error('Not a file: ): "{}"'.format(self._filename))

  def __str__(self):
    return str(self._config)

  @cached_property
  def _config(self):
    if not path.exists(self._filename):
      file_util.save(self._filename, content = '', codec = 'utf-8')
    return simple_config.from_file(self._filename,
                                   check_env_vars = False,
                                   entry_parser = self._parse_ssh_config_entry,
                                   entry_formatter = self._ssh_config_entry_formatter)
  
  def update_host(self, hostname, values):
    """
    Update a host with values.  Add it if needed.

    hostname (str): The hostname
    values (key_value_list, dict, or str): The values for hostname

    Returns None
    """
    check.check_string(hostname)

    section = self.find_host(hostname)
    if not section:
      section = self._config.add_section('Host', extra_text = hostname)
    section.clear_values()
    section.set_values(values, hints = { 'delimiter': ' ' })
    self._save()

  def find_host(self, hostname):
    'Find and return section for hostname or None if not found.'
    check.check_string(hostname)

    return self._config.find_first_section(hostname, matcher = lambda section, hostname: section.header_.extra_text == hostname)
    
  def _save(self):
    file_util.save(self._filename,
                   content = str(self._config),
                   mode = 0o0600,
                   codec = 'utf-8')
      
  @classmethod
  def _parse_ssh_config_entry(clazz, text, origin, validate_key_characters = True):
    check.check_string(text)
    check.check_simple_config_origin(origin)
    hints = {}
    if '=' in text:
      kv = key_value.parse(text)
      hints['delimiter'] = '='
    else:
      parts = string_util.split_by_white_space(text, strip = True)
      if len(parts) < 2:
        raise simple_config_error('invalid sss config entry (not enough parts): "{}"'.format(text), origin)
      kv = key_value(parts.pop(0), ' '.join(parts))
      hints['delimiter'] = ' '
    return simple_config_entry(kv, origin = origin, hints = hints)

  @classmethod
  def _ssh_config_entry_formatter(clazz, entry, sort = False, key_column_width = 0):
    assert entry.hints
    assert 'delimiter' in entry.hints
    return entry.value.to_string(delimiter = entry.hints['delimiter'])
