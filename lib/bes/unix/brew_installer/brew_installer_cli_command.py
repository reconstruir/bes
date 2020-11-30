#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.argparser_handler import argparser_handler
from bes.common.check import check
from bes.fs.file_util import file_util

from .brew_installer import brew_installer
from .brew_installer_options import brew_installer_options

class brew_installer_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    options = brew_installer_options(**kargs)
    filtered_args = argparser_handler.filter_keywords_args(brew_installer_options, kargs)
    func = getattr(brew_installer_cli_command, command)
    return func(options, **filtered_args)
  
  @classmethod
  def run_script(clazz, options, script_name, args, print_only):
    check.check_brew_installer_options(options)
    check.check_string(script_name)
    check.check_string_seq(args, allow_none = True)
    check.check_bool(print_only)
    
    if print_only:
      tmp = brew_installer.download_script(script_name)
      file_util.page(tmp)
      return 0
    brew_installer.run_script(script_name, args, options)
    return 0

  @classmethod
  def info(clazz, options):
    check.check_brew_installer_options(options)

    version = brew_installer.version()
    print(version)
    return 0

  @classmethod
  def reinstall(clazz, options):
    check.check_brew_installer_options(options)

    brew_installer.reinstall(options)
    return 0
  
  @classmethod
  def install(clazz, options):
    check.check_brew_installer_options(options)

    brew_installer.install(options)
    return 0

  @classmethod
  def uninstall(clazz, options):
    check.check_brew_installer_options(options)

    brew_installer.uninstall(options)
    return 0

  @classmethod
  def ensure(clazz, options):
    check.check_brew_installer_options(options)

    brew_installer.ensure(options)
    return 0
  
