#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.cli.cli_helper import cli_helper
from bes.fs.file_util import file_util

from .egg import egg

class egg_cli_handler(cli_helper):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(egg_cli_handler, command)
    return func(**kargs)
  
  @classmethod
  def make(clazz, root_dir, setup_filename, revision, output_dir, untracked, verbose, debug):
    root_dir = clazz.resolve_dir(root_dir)
    resolved_setup_filename = clazz.resolve_file(setup_filename, root_dir = root_dir)
    clazz.check_dir(root_dir)
    clazz.check_file(resolved_setup_filename)
    clazz.check_dir(output_dir)
    tmp_egg = egg.make(root_dir, revision, setup_filename, untracked = untracked, debug = debug)
    dst_egg = file_util.relocate_file(tmp_egg, output_dir)
    if verbose:
      print(dst_egg)
    return 0

  @classmethod
  def unpack(clazz, egg_filename, output_dir, verbose):
    egg_filename = clazz.resolve_file(egg_filename)
    clazz.check_file(egg_filename)
    clazz.check_dir(output_dir)
    egg.unpack(egg_filename, output_dir)
    return 0
