#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.argparser_handler import argparser_handler
from bes.common.check import check

from .brew import brew
from .brew_options import brew_options

class brew_cli_handler(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    options = brew_options(**kargs)
    filtered_args = argparser_handler.filter_keywords_args(brew_options, kargs)
    func = getattr(brew_cli_handler, command)
    return func(options, **filtered_args)
  
  @classmethod
  def info(clazz, options):
    check.check_brew_options(options)

    version = brew.version()
    print('version: {}'.format(version))
    return 0

  @classmethod
  def installed(clazz, options):
    check.check_brew_options(options)

    installed = brew.installed()
    for p in installed:
      print(p)
    return 0
  
  @classmethod
  def available(clazz, options):
    check.check_brew_options(options)

    available = brew.available()
    for p in available:
      print(p)
    return 0
  
