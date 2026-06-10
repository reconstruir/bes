#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check

from .properties_editor import properties_editor

class properties_file_command_handler(bcli_command_handler):

  def name(self):
    return 'properties_file'

  def _command_set(self, filename, key, value, options):
    check.check_string(filename)
    check.check_string(key)
    check.check_string(value)

    editor = properties_editor(filename)
    editor.set_value(key, value)
    return 0

  def _command_get(self, filename, key, options):
    check.check_string(filename)
    check.check_string(key)

    if not path.isfile(filename):
      raise IOError('file not found: {}'.format(filename))
    editor = properties_editor(filename)
    value = editor.get_value(key)
    print(value)
    return 0

  def _command_bump_version(self, filename, key, component, options):
    check.check_string(filename)
    check.check_string(key)
    check.check_string(component)

    if not path.isfile(filename):
      raise IOError('file not found: {}'.format(filename))
    editor = properties_editor(filename)
    editor.bump_version(key, component)
    return 0

  def _command_change_version(self, filename, key, component, value, options):
    check.check_string(filename)
    check.check_string(key)
    check.check_string(component)

    if not path.isfile(filename):
      raise IOError('file not found: {}'.format(filename))
    editor = properties_editor(filename)
    editor.change_version(key, component, value)
    return 0
