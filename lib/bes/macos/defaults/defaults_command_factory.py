#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_base import bcli_command_factory_base

from .defaults_command_handler import defaults_command_handler

class defaults_command_factory(bcli_command_factory_base):

  @classmethod
  def path(clazz):
    return 'defaults'

  @classmethod
  def description(clazz):
    return 'Deal with defaults'

  def error_class(self):
    raise RuntimeError

  def options_class(self):
    return None

  def has_commands(self):
    return True

  def add_arguments(self, parser):
    pass

  def add_commands(self, subparsers):
    p = subparsers.add_parser('get_domain', help = 'Read a whole domain.')
    p.add_argument('domain', action = 'store', default = None,
                   help = 'The domain [ None ]')
    p.add_argument('-s', '--style', action = 'store', default = 'json',
                   choices = ( 'raw', 'json', 'plist' ),
                   help = 'The output style. Either json or raw [ json ]')

    p = subparsers.add_parser('get_value', help = 'Read a value.')
    p.add_argument('domain', action = 'store', default = None,
                   help = 'The domain [ None ]')
    p.add_argument('key', action = 'store', default = None,
                   help = 'The key [ None ]')

    p = subparsers.add_parser('set_value', help = 'Set a value.')
    p.add_argument('domain', action = 'store', default = None,
                   help = 'The domain [ None ]')
    p.add_argument('key', action = 'store', default = None,
                   help = 'The key [ None ]')
    p.add_argument('value', action = 'store', default = None,
                   help = 'The value [ None ]')

  def handler_class(self):
    return defaults_command_handler

  def supported_platforms(self):
    return 'darwin'
