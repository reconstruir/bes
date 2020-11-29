#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.object_util import object_util
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.system.which import which
from bes.text.tree_text_parser import tree_text_parser
from bes.text.text_line_parser import text_line_parser

from .softwareupdater_item import softwareupdater_item
from .softwareupdater_error import softwareupdater_error

class softwareupdater(object):
  'Class to deal with the macos softwareupdate program.'

  _log = logger('softwareupdater')
  
  @classmethod
  def available(clazz):
    'Return a list of available software update items.'
    host.check_is_macos()

    rv = clazz._call_softwareupdate('--list', False)
    return clazz._parse_list_output(rv.stdout)

  @classmethod
  def _parse_list_output(clazz, text):
    'Parse the output of softwareupdate --list.'
    result = []
    seen_labels = set()
    lp = text_line_parser(text)

    found = lp.match_first(r'^Software Update found the following.*$')
    if not found:
      return []

    matches = lp.match_all(r'^\s*\*.*$')
    for label_line in matches:
      attribute_index = lp.find_by_line_number(label_line.line_number + 1)
      assert attribute_index >= 0
      attributes_line = lp[attribute_index]
      if 'Label' in label_line.text:
        item = clazz._parse_item_catalina(label_line, attributes_line)
      else:
        item = clazz._parse_item_mojave(label_line, attributes_line)
      if not item.label in seen_labels:
        result.append(item)
        seen_labels.add(item.label)
    return sorted(result)
  
  @classmethod
  def install(clazz, label, verbose):
    'Install an item by label.'
    check.check_string(label)
    check.check_bool(verbose)

    args = [
      '--verbose',
      '--install',
      #'--agree-to-license', # big sur only
      '"{}"'.format(label),
    ]
    clazz._call_softwareupdate(args, verbose)

  @classmethod
  def _parse_item_catalina(clazz, label_line, attributes_line):
    label = clazz._parse_label_catalina(label_line.text)
    title, attributes = clazz._parse_attributes_catalina(attributes_line.text)
    item = softwareupdater_item(label, title, attributes)
    return item
    
  _LABEL_PATTERN_CATALINA = r'^\s*\*\s+Label:\s+(.+)\s*$'
  @classmethod
  def _parse_label_catalina(clazz, text):
    f = re.findall(clazz._LABEL_PATTERN_CATALINA, text)
    assert len(f) == 1
    return f[0]
                                     
  _ATTRIBUTES_PATTERN_CATALINA = r'^\s*Title:\s+(.+),\s+Version:\s+(.+),\s+Size:\s+(.+),\s+Recommended:\s+(.+),\s*$'
  @classmethod
  def _parse_attributes_catalina(clazz, text):
    f = re.findall(clazz._ATTRIBUTES_PATTERN_CATALINA, text)
    assert len(f) == 1
    assert len(f[0]) == 4
    t = f[0]
    title = t[0]
    return title, {
      'version': t[1],
      'size': t[2],
      'recommended': t[3].lower() == 'yes',
    }

  @classmethod
  def _parse_item_mojave(clazz, label_line, attributes_line):
    label = clazz._parse_label_mojave(label_line.text)
    title, attributes = clazz._parse_attributes_mojave(attributes_line.text)
    item = softwareupdater_item(label, title, attributes)
    return item

  _LABEL_PATTERN_MOJAVE = r'^\s*\*\s+(.+)\s*$'
  @classmethod
  def _parse_label_mojave(clazz, text):
    f = re.findall(clazz._LABEL_PATTERN_MOJAVE, text)
    assert len(f) == 1
    return f[0]
  
  _ATTRIBUTES_PATTERN_MOJAVE = r'^\s*(.+)\s+\((.+)\),\s+(.+K)\s+(.+)\s*$'
  @classmethod
  def _parse_attributes_mojave(clazz, text):
    f = re.findall(clazz._ATTRIBUTES_PATTERN_MOJAVE, text)
    assert len(f) == 1
    assert len(f[0]) == 4
    t = f[0]
    title = t[0]
    attributes_text = t[3].lower()
    attributes = {
      'version': t[1],
      'size': t[2],
    }
    if '[recommended]' in attributes_text:
      attributes['recommended'] = True
    if '[restart]' in attributes_text:
      attributes['restart'] = True
    return title, attributes
  
  @classmethod
  def _call_softwareupdate(clazz, args, verbose):
    check.check_string_seq(args)
    check.check_bool(verbose)

    command_line.check_args_type(args)
    args = object_util.listify(args)

    exe = which.which('softwareupdate')
    if not exe:
      raise softwareupdater_error('softwareupdate not found')
    
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
      raise softwareupdater_error(msg, status_code = rv.exit_code)
    return rv


#  14
#  
#   * Safari14.0.1MojaveAuto-14.0.1
#	Safari (14.0.1), 67518K [recommended]
#   * Security Update 2020-005-10.14.6
#	Security Update 2020-005 (10.14.6), 1633218K [recommended] [restart]
#   * Safari14.0MojaveAuto-10.14.6
#	macOS Supplemental Update (10.14.6), 67310K [recommended] [restart]
#   * Command Line Tools (macOS Mojave version 10.14) for Xcode-10.3
#	Command Line Tools (macOS Mojave version 10.14) for Xcode (10.3), 199250K [recommended]
  
