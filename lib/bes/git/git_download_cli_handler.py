#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.cli.cli_command_handler import cli_command_handler

from .git_download import git_download
from .git_download_options import git_download_options
from .git_output import git_output
from .git_util import git_util

class git_download_cli_handler(cli_command_handler):

  def __init__(self, cli_args):
    super(git_download_cli_handler, self).__init__(cli_args, options_class = git_download_options)
    check.check_git_download_options(self.options)
  
  def fetch(self, address, revision, output_filename):
    check.check_string(address)
    check.check_string(revision)
    check.check_string(output_filename, allow_none = True)

    output_filename = git_download.download(address,
                                            revision,
                                            output_filename = output_filename,
                                            base_name = None,
                                            download_options = self.options)
    if self.options.verbose:
      print('Downloaded {}/{} to {}'.format(address, revision, output_filename))
    return 0

  def available(self, address, prefix, limit, sort_type, reverse):
    check.check_string(address)
    check.check_int(limit, allow_none = True)
    check.check_string(prefix, allow_none = True)
    check.check_string(sort_type, allow_none = True)
    check.check_bool(reverse)

    tags = git.list_remote_tags_for_address(address,
                                            sort_type = sort_type,
                                            reverse = reverse,
                                            limit = limit, prefix = prefix)
    tags.output('brief', output_filename = None)
    return 0
