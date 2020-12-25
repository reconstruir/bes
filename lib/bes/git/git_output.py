#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.fs.file_util import file_util

class git_output(object):
  
  @classmethod
  def output_string(clazz, s, options):
    check.check_string(s)
    check.check_git_cli_common_options(options)
    with file_util.open_with_default(filename = options.output_filename) as f:
      f.write(s)
      f.write('\n')
