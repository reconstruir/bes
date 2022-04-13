#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from ..system.check import check
from bes.fs.file_util import file_util
from bes.git.git import git
from bes.git.git_error import git_error

from .refactor_operation_type import refactor_operation_type

class refactor_item(namedtuple('refactor_item', 'src, dst')):

  def __new__(clazz, src, dst):
    check.check_string(src)
    check.check_string(dst)
    
    return clazz.__bases__[0].__new__(clazz, src, dst)

  def __str__(self):
    return f'{self.src} => {self.dst}'

  def __repr__(self):
    return str(self)

  def apply_operation(self, operation, try_git):
    check.check_refactor_operation_type(operation)
    check.check_bool(try_git)
    
    if operation == refactor_operation_type.COPY_FILES:
      self._apply_operation_copy(try_git)
    elif operation in [ refactor_operation_type.RENAME_FILES, refactor_operation_type.RENAME_DIRS ]:
      self._apply_operation_rename(try_git)

  _is_safe_result = namedtuple('_is_safe_result', 'safe, reason')
  def is_safe(self, operation):
    check.check_refactor_operation_type(operation)

    if operation == refactor_operation_type.COPY_FILES:
      if path.exists(self.dst):
        return self._is_safe_result(False, f'Copied destination exists: {self.dst}')
    elif operation in [ refactor_operation_type.RENAME_FILES, refactor_operation_type.RENAME_DIRS ]:
      if path.exists(self.dst):
        return self._is_safe_result(False, f'Renamed destination exists: {self.dst}')
    return self._is_safe_result(True, None)
      
  def _apply_operation_rename(self, try_git):
    git_worked = False
    if try_git:
      root_dir = git.find_root_dir(start_dir = path.dirname(self.src))
      should_ignore = git.check_ignore(root_dir, self.src)
      if not should_ignore:
        try:
          git.move(root_dir, self.src, self.dst)
          git_worked = True
        except git_error as ex:
          print(f'caught: {ex}')
    if not git_worked:
      file_util.rename(self.src, self.dst)

  def _apply_operation_copy(self, try_git):
    file_util.copy(self.src, self.dst)
    file_util.copy_mode(self.src, self.dst)
    if try_git:
      root_dir = git.find_root_dir(start_dir = path.dirname(self.dst))
      should_ignore = git.check_ignore(root_dir, self.src)
      if not should_ignore:
        try:
          git.add(root_dir, [ self.dst ])
        except git_error as ex:
          print(f'caught: {ex}')
      
check.register_class(refactor_item, include_seq = False)
