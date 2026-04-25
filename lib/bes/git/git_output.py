#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.files.bf_file_ops import bf_file_ops

class git_output(object):
  
  @classmethod
  def output_string(clazz, s, options):
    check.check_string(s)
    check.check_git_cli_common_options(options)
    with bf_file_ops.open_with_default(filename = options.output_filename) as f:
      f.write(s)
      f.write('\n')
