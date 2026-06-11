#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

class _dirs_cli_options_desc(bcli_options_desc):

  def _options_desc(self):
    return '''
    debug  bool  default=False
  dry_run  bool  default=False
    quiet  bool  default=False
recursive  bool  default=False
  verbose  bool  default=False
'''

class dirs_cli_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_dirs_cli_options_desc(), **kwargs)

dirs_cli_options.register_check_class()
