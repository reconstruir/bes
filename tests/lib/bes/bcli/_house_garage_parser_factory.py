#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.bcli.bcli_command_factory_i import bcli_command_factory_i

class _house_garage_parser_factory(bcli_command_factory_i):

  @classmethod
  #@abstractmethod
  def path(clazz):
    return 'house/garage'

  @classmethod
  #@abstractmethod
  def description(clazz):
    return 'deal with the garage'
  
  #@abstractmethod
  def error_class(self):
    raise RuntimeError

  #@abstractmethod
  def options_class(self):
    return None
  
  #@abstractmethod
  def has_commands(self):
    return True
  
  #@abstractmethod
  def add_commands(self, subparsers):
    p = subparsers.add_parser('clean', help = 'Clean the garage.')
    p.add_argument('--method', action = 'store', type = str, default = 'vacuum',
                   choices = ( 'vacuum', 'sweep' ),
                   help = 'Cleaning method [ vacuum ]')

    p = subparsers.add_parser('close', help = 'Close the garage.')

  #@abstractmethod
  def add_arguments(self, parser):
    parser.add_argument('--output', action = 'store', type = str, default = 'json',
                        choices = ( 'json', 'text' ),
                        help = 'Output style [ json ]')

  #@abstractmethod
  def handler_class(self):
    from _house_garage_command_handler import _house_garage_command_handler
    return _house_garage_command_handler
    
