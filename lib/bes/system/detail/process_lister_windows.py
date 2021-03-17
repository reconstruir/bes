#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import csv

from bes.system.execute import execute
from bes.compat.StringIO import StringIO
from bes.system.process_info import process_info
from bes.windows.handle.handle import handle

from .process_lister_base import process_lister_base

class process_lister_windows(process_lister_base):

  @classmethod
  #@abstractmethod
  def list_processes(clazz):
    'List all processes.'

    # tasklist fields:
    # "Image Name"
    # "PID"
    # "Session Name"
    # "Session#"
    # "Mem Usage"
    # "Status"
    # "User Name"
    # "CPU Time"
    # "Window Title"
    rv = execute.execute('tasklist /V /NH /FO csv')
    stream = StringIO(rv.stdout)
    reader = csv.reader(stream, delimiter = ',')
    result = []
    for row in reader:
      row = row[:]
      image_name = row.pop(0)
      pid = row.pop(0)
      session_name = row.pop(0)
      session_number = row.pop(0)
      mem_usage = row.pop(0)
      status = row.pop(0)
      user_name = clazz._fix_na_strings(row.pop(0))
      cpu_time = row.pop(0)
      window_title = clazz._fix_na_strings(row.pop(0))
      other = {
        'window_title': window_title,
        'status': status,
        'session_number': session_number,
        'session_name': session_name,
      }
      info = process_info(user_name, pid, cpu_time, mem_usage, image_name, other)
      result.append(info)
    return result

  @classmethod
  def _fix_na_strings(clazz, s):
    if not s:
      return s
    if s == 'N/A':
      return None
    return s

  @classmethod
  #@abstractmethod
  def open_files(clazz, pid):
    'Return a list of open files for pid or None if pid not found.'

    handles = handle.open_handles(pid)
    assert len(handles) == 1
    items = handles[0].items
    return sorted([ item.target for item in items if item.handle_type == 'file' ])
