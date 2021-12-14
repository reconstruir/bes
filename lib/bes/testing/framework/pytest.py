#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.system.execute import execute

from .unit_test_description import unit_test_description

class pytest(object):

  @classmethod
  def inspect_files(clazz, files):
    cmd = [ 'pytest', '--collect-only', '--quiet' ] + list(files)
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code == 2:
      rv.raise_error(log_error = True, print_error = True)
    if rv.exit_code != 0:
      return []
    lines = [ line for line in rv.stdout_lines() if ' collected in ' not in line ]
    result = []
    for line in lines:
      parts = line.split('::')
      if len(parts) == 3:
        filename = parts[0]
        fixture = parts[1]
        function = parts[2]
        result.append(unit_test_description(path.abspath(filename), fixture, function))
    return result
