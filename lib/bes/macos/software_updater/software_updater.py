#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.object_util import object_util
from bes.fs.file_util import file_util
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.system.which import which
from bes.text.tree_text_parser import tree_text_parser

from .software_updater_item import software_updater_item
from .software_updater_error import software_updater_error

class software_updater(object):
  'Class to deal with the macos softwareupdate program.'

  _log = logger('software_updater')
  
  # touching this file forces softwareupdate to list the xcode command line tools
  _FORCE_COMMAND_LINE_TOOLS_FILE = '/tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress'
  
  @classmethod
  def available(clazz, force_command_line_tools):
    'Return a list of available software update items.'
    check.check_bool(force_command_line_tools)

    host.check_is_macos()

    if force_command_line_tools:
      file_util.save(clazz._FORCE_COMMAND_LINE_TOOLS_FILE)

    try:
      rv = clazz._call_softwareupdate('--list', False)
      return clazz._parse_list_output(rv.stdout)
    finally:
      if force_command_line_tools:
        file_util.remove(clazz._FORCE_COMMAND_LINE_TOOLS_FILE)
  
  @classmethod
  def _parse_list_output(clazz, text):
    'Parse the output of softwareupdate --list.'
    result = []
    root = tree_text_parser.parse(text)
    for child in root.children:
      text = child.data.text
      if text.startswith('* Label'):
        assert len(child.children) == 1
        label = clazz._parse_label(text)
        title, version, size, recommended = clazz._parse_attributes(child.children[0])
        item = software_updater_item(title, label, version, size, recommended == 'YES')
        result.append(item)
    return sorted(algorithm.unique(result))

  @classmethod
  def install(clazz, label):
    'Install an item by label.'
    check.check_string(label)

    '--install'
  
  _LABEL_PATTERN = r'^\* Label:\s+(.+)\s*$'
  @classmethod
  def _parse_label(clazz, text):
    f = re.findall(clazz._LABEL_PATTERN, text)
    assert len(f) == 1
    return f[0]
                                     
  _ATTRIBUTES_PATTERN = r'^Title:\s+(.+),\s+Version:\s+(.+),\s+Size:\s+(.+),\s+Recommended:\s+(.+),\s*$'
  @classmethod
  def _parse_attributes(clazz, node):
    f = re.findall(clazz._ATTRIBUTES_PATTERN, node.data.text)
    assert len(f) == 1
    assert len(f[0]) == 4
    return f[0]

  @classmethod
  def _call_softwareupdate(clazz, args, verbose):
    check.check_string_seq(args)
    check.check_bool(verbose)

    command_line.check_args_type(args)
    args = object_util.listify(args)

    exe = which.which('softwareupdate')
    if not exe:
      raise software_updater_error('softwareupdate not found')
    
    clazz._log.log_d('_call_softwareupdate: exe={} args={}'.format(exe, args))
    
    cmd = [ exe ] + args
    env = os_env.clone_current_env()
    rv = execute.execute(cmd,
                         env = env,
                         stderr_to_stdout = True,
                         raise_error = False,
                         non_blocking = verbose)
    if rv.exit_code != 0:
      cmd_flat = ' '.join(cmd)
      msg = 'softwareupdate command failed: {} - {}\n{}'.format(cmd,
                                                                rv.exit_code,
                                                                rv.stdout)
      raise software_updater_error(msg, status_code = rv.exit_code)
    return rv