#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from enum import IntEnum
from os import path
import copy
import difflib
import os

from ..compat.StringIO import StringIO
from ..fs.dir_util import dir_util
from ..fs.file_util import file_util
from ..fs.temp_file import temp_file
from ..system.check import check
from ..system.env_var import env_var
from ..system.execute import execute
from ..system.log import logger
from ..system.os_env import os_env
from ..text.text_line_parser import text_line_parser


class action(IntEnum):
  SET = 1
  UNSET = 2
  PATH_APPEND = 3
  PATH_PREPEND = 4
  PATH_REMOVE = 5

instruction = namedtuple('instruction', 'key, value, action')
  
class env_dir(object):

  _log = logger('env_dir')
  
  def __init__(self, root_dir, files = None, debug = False):
    self._root_dir = path.abspath(root_dir)
    self._files = self._determine_files(self._root_dir, files)
    self._debug = debug
    self._log.log_i(f'env_dir.__init__: root_dir={root_dir} debug={debug}')
    self._log.log_d(f'env_dir.__init__: files={os.linesep.join(files or [])}', multi_line=True)
    self._log.log_d(f'env_dir.__init__: resolved_files={os.linesep.join(self._files)}', multi_line=True)
    
  @classmethod
  def _determine_files(clazz, root_dir, files):
    if files:
      for f in files:
        p = path.join(root_dir, f)
        if not path.isfile(p):
          raise IOError('File not found: %s' % (p))
      return files
    else:
      return dir_util.list(root_dir, relative = True, patterns = [ '*.sh' ], basename = True)

  @property
  def files(self):
    return self._files

  @property
  def files_abs(self):
    return [ path.join(self._root_dir, f) for f in self.files ]

  @classmethod
  def transform_env(clazz, env, instructions):
    for i, inst in enumerate(instructions, start = 1):
      clazz._log.log_d(f'transform_env: instruction {i}: {inst.action.name}:{inst.key}:{inst.value}')
    new_env = copy.deepcopy(env)
    for inst in instructions:
      if inst.action == action.SET:
        v = env_var(new_env, inst.key)
        old_value = v.value
        v.value = inst.value
        new_value = v.value
        clazz._log.log_d(f'transform_env: SET:{inst.key}:{inst.value} old_value={old_value} new_value={new_value}')        
        new_env[inst.key] = inst.value
      elif inst.action == action.UNSET:
        if inst.key in new_env:
          clazz._log.log_d(f'transform_env: UNSET:{inst.key}:{inst.value} value={inst.value}')
          del new_env[inst.key]
      elif inst.action == action.PATH_APPEND:
        v = env_var(new_env, inst.key)
        old_value = v.value
        v.append(inst.value)
        new_value = v.value
        clazz._log.log_d(f'transform_env: PATH_APPEND:{inst.key}:{inst.value} old_value={old_value} new_value={new_value}')
      elif inst.action == action.PATH_PREPEND:
        v = env_var(new_env, inst.key)
        old_value = v.value
        v.prepend(inst.value)
        new_value = v.value
        clazz._log.log_d(f'transform_env: PATH_PREPEND:{inst.key}:{inst.value} old_value={old_value} new_value={new_value}')
      elif inst.action == action.PATH_REMOVE:
        v = env_var(new_env, inst.key)
        old_value = v.value
        v.remove(inst.value)
        new_value = v.value
        clazz._log.log_d(f'transform_env: PATH_REMOVE:{inst.key}:{inst.value} old_value={old_value} new_value={new_value}')
    return new_env
    
  def instructions(self, env):
    buf = StringIO()
    buf.write('#!/bin/bash\n')
    buf.write('echo "----1----"\n')
    buf.write('declare -px\n')
    buf.write('echo "----2----"\n')
    for filename in self.files_abs:
      buf.write(f'source \"{filename}\"\n')
    buf.write('echo "----3----"\n')
    buf.write('declare -px\n')
    buf.write('echo "----4----"\n')
    script_content = buf.getvalue()
    self._log.log_d(f'instructions: script_content={script_content}', multi_line = True)
    script = temp_file.make_temp_file(content = script_content, delete = not self._debug, perm = 0o755)
    self._log.log_d(f'instructions: script={script}')
    try:
      rv = execute.execute(script, raise_error = True, shell = True, env = env)
    finally:
      if not self._debug:
        file_util.remove(script)
    parser = text_line_parser(rv.stdout)
    self._log.log_d(f'instructions: stdout={rv.stdout}', multi_line = True)
    self._log.log_d(f'instructions: stderr={rv.stderr}', multi_line = True)
    if rv.stderr:
      rv.raise_error(log_error = True, tag = self._log.tag)
    env1 = self._parse_env_lines(parser.cut_lines('----1----', '----2----'))
    for key, value in sorted(env1.items()):
      self._log.log_d(f'instructions: ENV1: {key}="{value}"')
    env2 = self._parse_env_lines(parser.cut_lines('----3----', '----4----'))
    for key, value in sorted(env2.items()):
      self._log.log_d(f'instructions: ENV2: {key}="{value}"')
    delta = self._env_delta(env1, env2)
    for key in sorted(delta.added):
      self._log.log_d(f'instructions: DELTA ADDED: {key}')
    for key in sorted(delta.removed):
      self._log.log_d(f'instructions: DELTA REMOVED: {key}')
    for key in sorted(delta.changed):
      self._log.log_d(f'instructions: DELTA CHANGED: {key}')

    added_instructions = []
    for key in delta.added:
      added_instructions.append(instruction(key, env2[key], action.SET))
    added_instructions = sorted(added_instructions, key = lambda inst: inst.key)
      
    removed_instructions = []
    for key in delta.removed:
      removed_instructions.append(instruction(key, None, action.UNSET))
    removed_instructions = sorted(removed_instructions, key = lambda inst: inst.key)

    changed_instructions = {}
    for key in delta.changed:
      value1 = env1[key]
      value2 = env2[key]
      self._log.log_d(f'instructions: CHANGED: key={key} value1={value1} value2={value2}')
      assert key not in changed_instructions
      changed_instructions[key] = []
      for inst in self._determine_change_instructions(key, value1, value2):
        self._log.log_d(f'instructions: CHANGED: inst={inst}')
        changed_instructions[key].append(inst)

    result = []
    result.extend(added_instructions)
    result.extend(removed_instructions)
    for key in sorted([ key for key in changed_instructions.keys() ]):
      next_changed = changed_instructions[key]
      result.extend(next_changed)
    for i, inst in enumerate(result, start = 1):
      self._log.log_d(f'instructions: RESULT: {i} {inst.action.name}:{inst.key}:{inst.value}')
    return result
      
  @classmethod
  def _parse_env_lines(clazz, lines):
    result = {}
    for line in lines:
      key, value = clazz.parse_bash_declare_output(line.text)
      result[key] = value
    return result

  _DECLARE_MARKER = 'declare -x '
  @classmethod
  def parse_bash_declare_output(clazz, text):
    assert text.startswith(clazz._DECLARE_MARKER)
    text = text[len(clazz._DECLARE_MARKER):]
    equal_pos = text.find('=')
    if equal_pos < 0:
      return text, ''
    key, delimiter, value = text.partition('=')
    assert delimiter == '='
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
      value = value[1:-1]      
    return key, value
      
  _delta = namedtuple('_delta', 'added, removed, changed')
  @classmethod
  def _env_delta(clazz, env1, env2):
    'Return delta between env1 and env2.'
    changed = set()
    keys1 = set([ key for key in env1.keys()])
    keys2 = set([ key for key in env2.keys()])
    added = keys2 - keys1
    removed = keys1 - keys2
    common = keys1 & keys2
    for key in common:
      value1 = env1[key]
      value2 = env2[key]
      if value1 != value2:
        clazz._log.log_d(f'_env_delta: {key} changed from "{value1}" to "{value2}"')
        changed.add(key)
    return clazz._delta(added, removed, changed)

  @classmethod
  def _determine_change_instructions(clazz, key, value1, value2):
    key_is_path = os_env.key_is_path(key)
    clazz._log.log_d(f'_determine_change_instructions: key={key} value1="{value1}" value2="{value2}" key_is_path={key_is_path}')
    if not key_is_path:
      yield instruction(key, value2, action.SET)
      
    p1 = env_var.path_split(value1)
#    p1.insert(0, '@@@HEAD@@@')
#    p1.append('@@@TAIL@@@')
    p2 = env_var.path_split(value2)
    clazz._log.log_d(f'_determine_change_instructions: p1={p1} p2={p2}')
    sm = difflib.SequenceMatcher(isjunk = None, a = p1, b = p2)

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
      clazz._log.log_d(f'_determine_change_instructions: tag={tag} i1={i1} i2={i2} j1={j1} j2={j2}')
      if tag == 'insert':
        if i1 == 0:
          for p in reversed(p2[j1:j2]):
            yield instruction(key, p, action.PATH_PREPEND)
        else:
          for p in p2[j1:j2]:
            yield instruction(key, p, action.PATH_APPEND)
      elif tag == 'delete':
        for p in p1[i1:i2]:
          yield instruction(key, p, action.PATH_REMOVE)
      elif tag == 'replace':
        for p in p1[i1:i2]:
          yield instruction(key, p, action.PATH_REMOVE)
        for p in p2[j1:j2]:
          yield instruction(key, p, action.PATH_APPEND)
      else:
        clazz._log.log_e(f'_determine_change_instructions: unhandled diff tag {tag}')
