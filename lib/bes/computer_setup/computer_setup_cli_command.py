#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, pprint

from bes.cli.argparser_handler import argparser_handler
from bes.common.Script import Script
from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.fs.file_path import file_path
from bes.script.blurber import blurber

from .computer_setup_error import computer_setup_error
from .computer_setup_manager import computer_setup_manager
from .computer_setup_options import computer_setup_options

class computer_setup_cli_command(object):
  'computer_setup cli commands.'

  @classmethod
  def handle_command(clazz, command, **kargs):
    options = computer_setup_options(**kargs)
    csm = computer_setup_manager(options = options)
    filtered_args = argparser_handler.filter_keywords_args(computer_setup_options, kargs)
    func = getattr(computer_setup_cli_command, command)
    return func(csm, **filtered_args)
#    kargs = copy.deepcopy(kargs)
#    func = getattr(computer_setup_cli_command, command)
#    bl = blurber(Script.name())
#    verbose = kargs.pop('verbose')
#    bl.set_verbose(verbose)
#    np = computer_setup(bl)
#    return func(np, **kargs)
  
  @classmethod
  def update(clazz, csm, config_filename):
    check.check_computer_setup_manager(csm)
    check.check_string(config_filename)
    return 0
