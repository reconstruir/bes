#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import sys

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .properties_editor import properties_editor

class properties_file_cli_handler(cli_command_handler):
  'properties_file cli handler.'

  def __init__(self, cli_args):
    super(properties_file_cli_handler, self).__init__(cli_args)

  def set(self, filename, key, value):
    check.check_string(filename)
    check.check_string(key)
    check.check_string(value)
    
    editor = properties_editor(filename)
    editor.set_value(key, value)
    return 0
  
  def get(self, filename, key):
    check.check_string(filename)
    check.check_string(key)
    
    if not path.isfile(filename):
      raise IOError('file not found: {}'.format(filename))
    editor = properties_editor(filename)
    value = editor.get_value(key)
    print(value)
    return 0
  
  def bump_version(self, filename, key, component):
    check.check_string(filename)
    check.check_string(key)
    check.check_string(component)
    
    if not path.isfile(filename):
      raise IOError('file not found: {}'.format(filename))
    editor = properties_editor(filename)
    editor.bump_version(key, component)
    return 0
  
  def change_version(self, filename, key, component, value):
    check.check_string(filename)
    check.check_string(key)
    check.check_string(component)
    
    if not path.isfile(filename):
      raise IOError('file not found: {}'.format(filename))
    editor = properties_editor(filename)
    editor.change_version(key, component, value)
    return 0
