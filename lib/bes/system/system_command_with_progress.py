#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod

from .execute import execute
from .system_command import system_command

class system_command_with_progress(system_command):
  'system_command subclass for commands that emit parseable progress output.'

  @classmethod
  @abstractmethod
  def progress_source(clazz):
    'Which stream carries progress lines: "stdout", "stderr", or "both".'
    raise NotImplementedError('progress_source')

  @classmethod
  @abstractmethod
  def parse_progress_line(clazz, stdout_line, stderr_line):
    'Parse one readline tick; return a non-None value to emit it as an event.'
    raise NotImplementedError('parse_progress_line')

  @classmethod
  def call_command_with_progress(clazz, args, progress_cb=None, quote=True, **kwargs):
    exe = clazz._find_exe()
    static = clazz.static_args() or []
    cmd = [exe] + list(static) + list(args)
    progress_result = execute.execute_with_progress(
      cmd,
      line_parser=clazz.parse_progress_line,
      progress_cb=progress_cb,
      progress_source=clazz.progress_source(),
      raise_error=False,
      quote=quote,
      **kwargs,
    )
    if progress_result.result.exit_code != 0:
      raise clazz.error_class()(
        f'{clazz.exe_name()} failed: {progress_result.result.stderr}'
      )
    return progress_result.result
