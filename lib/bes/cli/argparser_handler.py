#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import copy, inspect

from bes.system.log import logger
from bes.common.check import check
from bes.common.inspect_util import inspect_util
from bes.system.log import log
from bes.fs.file_check import file_check
from bes.git.git import git

class argparser_handler(object):
  'A class to simplify the process of calling functions to handle argparser commands'

  @classmethod
  def main(clazz, log_tag, parser, handler_object, command_group = None):
    log = logger(log_tag)
    args = parser.parse_args()
    command_group = getattr(args, 'command_group', command_group)
    command = getattr(args, 'command', None)
    possible_names = clazz._possible_method_names(command_group, command)
    handler = clazz._find_handler(handler_object, possible_names)
    if not handler:
      raise RuntimeError('No method found for command: %s' % (' '.join(possible_names)))
    handler_spec = inspect_util.getargspec(handler)

    # If the arghandler has a keywords field, that means the user intends
    # to use the simplified interface where handler methods are implemented
    # generically with **kargs
    if hasattr(handler_spec, 'varkw'):
      keywords = getattr(handler_spec, 'varkw')
    elif hasattr(handler_spec, 'keywords'):
      keywords = getattr(handler_spec, 'keywords')
    else:
      raise RuntimeError('keywords attribute not found.')

    if keywords:
      dict_args = copy.deepcopy(args.__dict__)
      for key in [ 'command', 'command_group' ]:
        if key in dict_args:
          del dict_args[key]
      args_blurb = '; '.join([ '{}={}'.format(key, value) for key, value in sorted(dict_args.items()) ])
      log.log_d('calling {}({})'.format(handler.__name__, args_blurb))
      if handler.__name__.endswith(command):
        exit_code = handler(**dict_args)
      else:
        exit_code = handler(command, **dict_args)
      if not isinstance(exit_code, int):
        raise RuntimeError('Handler should return an int exit_code: %s' % (handler))
      log.log_d('{}() returns {}'.format(handler.__name__, exit_code))
    else:
      arg_names = handler_spec.args
      if arg_names[0] != 'self':
        raise RuntimeError('First argument should be \"self\": "{}"'.format(method_name))
      arg_names.pop(0)
      for arg_name in arg_names:
        if not hasattr(args, arg_name):
          source_filename = inspect.getsourcefile(handler)
          source_line = inspect.getsourcelines(handler)[-1]
          raise RuntimeError('{}:{}:{}: Missing argument: "{}"'.format(source_filename,
                                                                       source_line,
                                                                       handler.__name__,
                                                                       arg_name))
      args = [ getattr(args, arg_name) for arg_name in arg_names ]
      args_blurb = '; '.join([ '%s=%s' % (key, value) for ( key, value ) in zip(arg_names, args) ])
      log.log_d('calling %s(%s)' % (handler.__name__, args_blurb))
      exit_code = handler(*args)
      if not isinstance(exit_code, int):
        raise RuntimeError('Handler should return an int exit_code: %s' % (handler))
      log.log_d('{}() returns {}'.format(handler.__name__, exit_code))
    return exit_code

  @classmethod
  def _possible_method_names(clazz, command_group, command):
    if not command:
      assert command_group
      return [ clazz._handler_method_name(command_group, None) ]
    names = [ clazz._handler_method_name(None, command) ]
    if command_group:
      names.append(clazz._handler_method_name(command_group, command))
      names.append(clazz._handler_method_name(command_group, None))
    return names
  
  @classmethod
  def _find_handler(clazz, handler_object, names):
    for name in names:
      handler = getattr(handler_object, name, None)
      if handler:
        return handler
    return None
  
  @classmethod
  def _handler_method_name(clazz, command_group, command):
    if command_group and command:
      name = '%s_%s' % (command_group, command)
    elif command_group:
      name = command_group
    elif command:
      name = command
    else:
      assert False
    return '_command_%s' % (name)
  
  @classmethod
  def check_file(clazz, filename):
    file_check.check_file(filename)

  @classmethod
  def check_dir(clazz, dirname):
    file_check.check_dir(dirname)

  @classmethod
  def check_dir_is_git_repo(clazz, d):
    git.check_is_repo(d)

  @classmethod
  def resolve_file(clazz, filename, root_dir = None):
    '''
    Resolve a filename as follows:
     . expand ~ to $HOME
     . make it an absolute path
    '''
    if root_dir:
      filename = path.join(root_dir, filename)
    else:
      if '~' in filename:
        filename = path.expanduser(filename)
      if not path.isabs(filename):
        filename = path.abspath(filename)
    return filename

  @classmethod
  def resolve_dir(clazz, dirname, root_dir = None):
    return clazz.resolve_file(dirname, root_dir = root_dir)
  
  @classmethod
  def filter_keywords_args(clazz, clazz_for_instance, kargs):
    check.check_class(clazz)
    
    instance = clazz_for_instance()
    fields = [ field for field in dir(instance) if not field.startswith('_') ]
    copied_args = copy.deepcopy(kargs)
    for field in fields:
      if field in copied_args:
        del copied_args[field]
    return copied_args
