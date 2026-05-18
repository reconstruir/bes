#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple

from bes.system.system_command_with_progress import system_command_with_progress

from .bf_rsync_error import bf_rsync_error

rsync_progress = namedtuple('rsync_progress', 'bytes_done, percent, rate, elapsed')

_PROGRESS_RE = re.compile(r'^\s*(\S+)\s+(\d+)%\s+(\S+)\s+(\d+:\d+:\d+)')

class bf_rsync_command(system_command_with_progress):

  @classmethod
  def exe_name(clazz):
    return 'rsync'

  @classmethod
  def extra_path(clazz):
    return None

  @classmethod
  def error_class(clazz):
    return bf_rsync_error

  @classmethod
  def static_args(clazz):
    return None

  @classmethod
  def supported_systems(clazz):
    return ( 'linux', 'macos' )

  @classmethod
  def progress_source(clazz):
    return 'both'

  @classmethod
  def parse_progress_line(clazz, stdout_line, stderr_line):
    match = _PROGRESS_RE.match(stdout_line or stderr_line or '')
    if not match:
      return None
    return rsync_progress(
      bytes_done=match.group(1),
      percent=int(match.group(2)),
      rate=match.group(3),
      elapsed=match.group(4),
    )
