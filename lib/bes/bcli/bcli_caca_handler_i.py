#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import copy
#import inspect
#
#from bes.cli.argparser_handler import argparser_handler
from ..system.check import check
#from bes.common.inspect_util import inspect_util
#from bes.script.blurber import blurber
#
#from .bcli_missing_command_error import bcli_missing_command_error
#from .bcli_options import bcli_options

class bcli_caca_handler_i(object):

  def __init__(self): #, cli_args, options_class = None, delegate = None, label = None):
    pass
#    check.check_dict(cli_args)
#    check.check_class(options_class, allow_none = True)
#    check.check_callable(delegate, allow_none = True)
#    check.check_string(label, allow_none = True)
#
#    if delegate:
#      self._check_delegate(delegate)
#    
#    self._cli_args = cli_args
#    self._delegate = delegate
#    self.options, self._kwargs = self.make_options(options_class, cli_args)
#    self._blurber = blurber(label)
#
#  @classmethod
#  def make_options(clazz, options_class, cli_args):
#    check.check_dict(cli_args)
#    
#    if not options_class:
#      return None, copy.deepcopy(cli_args)
#    else:
#      options = options_class()
#      args = {}
#      for name, value in cli_args.items():
#        if options.has_option(name):
#          setattr(options, name, value)
#        else:
#          args[name] = value
#      if isinstance(options, bcli_options):
#        pass
#        #config_file_key = options.config_file_key()
#        #if config_file_key and config_file_key in args:
#        #  del args[config_file_key]
#      return options, args
#    
#  def handle_command(self, command_name):
#    if not command_name:
#      raise bcli_missing_command_error('{}.handle_command() - missing command'.format(self.__class__))
#    check.check_string(command_name)
#
#    if self._delegate:
#      args = ()
#      result = self._delegate(command_name, self.options, *args, **self._kwargs)
#    else:
#      func = getattr(self, command_name)
#      result = func(**self._kwargs)
#    return result
#
#  @classmethod
#  def _check_delegate(clazz, delegate):
#    spec = inspect_util.getargspec(delegate)
#
#    criteria = []
#    criteria.append(bool(spec.args))
#    criteria.append(len(spec.args) == 3)
#    criteria.append(bool(spec.varargs))
#    if hasattr(spec, 'keywords'):
#      criteria.append(bool(spec.keywords))
#    
#    if False in criteria:
#      msg = 'delegte signature should be exactly (self, command_name, options, *args, **kwargs) - {}'.format(delegate)
#      raise RuntimeError(msg)
#
#  def handle_boolean_result(self, result, verbose):
#    if verbose:
#      print(str(result))
#    return 0 if result else 1
#  
#  @property
#  def blurber(self):
#    return self._blurber
#  
#  def blurb(self, *args, **kargs):
#    self._blurber.blurb(*args, **kargs)
#
#  def blurb_verbose(self, *args, **kargs):
#    self._blurber.blurb_verbose(*args, **kargs)
##
