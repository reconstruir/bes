#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from ..system.check import check

from .dirs_cli_options import dirs_cli_options
from .file_check import file_check
from .file_find import file_find
from .file_resolver import file_resolver
from .file_resolver_options import file_resolver_options

class dirs_cli_handler(cli_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = dirs_cli_options)
    check.check_dirs_cli_options(self.options)
    self._resolver_options = file_resolver_options(recursive = self.options.recursive)
  
  def remove_empty(self, where):
    where = file_check.check_dir(where)
    max_depth = None if self.options.recursive else 1
    if self.options.dry_run:
      empties = file_find.find_empty_dirs(where, relative = False, max_depth = max_depth)
      for empty in empties:
        print(f'DRY_RUN: would remove {empty}')
    else:
      file_find.remove_empty_dirs(where, max_depth = max_depth)
      
    return 0
