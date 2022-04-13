#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.cli.cli_helper import cli_helper
from bes.cli.cli_command_handler import cli_command_handler
from bes.fs.file_util import file_util

from .egg import egg
from .egg_options import egg_options

class egg_cli_handler(cli_command_handler, cli_helper):

  def __init__(self, cli_args):
    super(egg_cli_handler, self).__init__(cli_args, options_class = egg_options)
    check.check_egg_options(self.options)
  
  def make_from_address(self, address, revision):
    check.check_string(address)
    check.check_string(revision)

    tmp_egg = egg.make_from_address(address, revision, options = self.options)
    dst_egg = file_util.relocate_file(tmp_egg, self.options.output_dir)
    if self.options.verbose:
      print(dst_egg)
    return 0

  @classmethod
  def unpack(clazz, egg_filename, output_dir, verbose):
    egg_filename = clazz.resolve_file(egg_filename)
    clazz.check_file(egg_filename)
    clazz.check_dir(output_dir)
    egg.unpack(egg_filename, output_dir)
    return 0
