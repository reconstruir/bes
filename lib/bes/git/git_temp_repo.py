#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect
from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.fs.temp_file import temp_file
from bes.fs.file_mode import file_mode
from bes.config.simple_config import simple_config

from .git_repo import git_repo
from .git_temp_repo_error import git_temp_repo_error

class _method_caller(object):

  def __init__(self, target, method_name):
    self.target = target
    self.method_name = method_name

  def __call__(self, *args, **kargs):
    method = getattr(self.target, self.method_name, None)
    assert method is not None
    assert callable(method)
    return method(*args, **kargs)

class git_temp_repo(object):
  '''
  A temp git repo for unit testing that is backed by a fake "remote" repo such
  that all operations mimic the behavior of working with a cloned repo.
  '''
  
  def __init__(self, remote = True, content = None, debug = False,
               prefix = None, commit_message = None):
    self._debug = debug
    if remote:
      self._init_remote(content, prefix, commit_message = commit_message)
    else:
      self._init_local(content, prefix, commit_message = commit_message)

  def _init_remote(self, content, prefix, commit_message = None):
    if prefix:
      remote_prefix = '{}remote-'.format(prefix)
    else:
      remote_prefix = 'remote-'
    self._remote_repo = self._make_temp_repo(init_args = [ '--bare', '--shared' ],
                                             debug = self._debug,
                                             prefix = remote_prefix,
                                             commit_message = commit_message)
    if prefix:
      local_prefix = '{}local-'.format(prefix)
    else:
      local_prefix = 'local-'
    tmp_dir = temp_file.make_temp_dir(delete = not self._debug, prefix = local_prefix)
    if self._debug:
      print('git_temp_repo: tmp_dir: %s' % (tmp_dir))
    self._local_repo = git_repo(tmp_dir, address = self._remote_repo.root)
    self._local_repo.clone()
    
    if content:
      self._local_repo.write_temp_content(items = content, commit = True, commit_message = commit_message)
      self._local_repo.push('origin', 'master')
    self.root = self._local_repo.root
    self.address = self._remote_repo.root
    self._transplant_methods(self._local_repo)

  @property
  def repo(self):
    return self._local_repo
    
  def _init_local(self, content, prefix, commit_message = None):
    tmp_dir = temp_file.make_temp_dir(delete = not self._debug, prefix = prefix)
    if self._debug:
      print('git_temp_repo: tmp_dir: %s' % (tmp_dir))
    self._local_repo = git_repo(tmp_dir, address = None)
    self._local_repo.init()
    if content:
      self._local_repo.write_temp_content(items = content, commit = True, commit_message = commit_message)
    self.root = self._local_repo.root
    self.address = None
    self._transplant_methods(self._local_repo)

  def _transplant_methods(self, target):
    method_names = [ attr for attr in dir(target) if inspect.ismethod(getattr(target, attr)) ]
    method_names = [ name for name in method_names if not name.startswith('_') ]
    for method_name in method_names:
      if hasattr(self, method_name):
        raise git_temp_repo_error('{} already has method \"{}\"'.format(self, method_name))
      setattr(self, method_name, _method_caller(target, method_name))
      
  def make_temp_cloned_repo(self, prefix = None):
    tmp_dir = temp_file.make_temp_dir(delete = not self._debug, prefix = prefix)
    if self._debug:
      print('git_temp_repo: tmp_dir: %s' % (tmp_dir))
    r = git_repo(tmp_dir, address = self._remote_repo.root)
    r.clone()
    return r
      
  @classmethod
  def _make_temp_repo(clazz, init_args = None, content = None, debug = False, prefix = None, commit_message = None):
    tmp_dir = temp_file.make_temp_dir(delete = not debug, prefix = prefix)
    if debug:
      print('git_temp_repo: tmp_dir: %s' % (tmp_dir))
    r = git_repo(tmp_dir, address = None)
    init_args = init_args or []
    r.init(*init_args)
    if content:
      check.check_string_seq(content)
      r.write_temp_content(content, commit = True, commit_message = commit_message)
    return r
  
  def apply_config_text(self, config_text):
    check.check_string(config_text)

    config = simple_config.from_text(config_text,
                                     source = '<git_temp_repo>',
                                     check_env_vars = False,
                                     validate_key_characters = False)
    cmds = []
    for section in config:
      cmd = self._command_parse(section)
      cmds.append(cmd)

    for cmd in cmds:
      self._command_apply(cmd)

  def _command_apply(self, cmd):
    handler_name = '_command_apply_{}'.format(cmd.command_name)
    if not hasattr(self, handler_name):
      raise git_temp_repo_error('unknown command apply: "{}"'.format(cmd.command_name))
    handler = getattr(self, handler_name)
    return handler(cmd)

  def _command_apply_file(self, cmd):
    assert cmd.command_name == 'file'
  
  def _command_apply_add(self, cmd):
    assert cmd.command_name == 'add'

  def _command_apply_tag(self, cmd):
    assert cmd.command_name == 'tag'
    
  def _command_apply_branch(self, cmd):
    assert cmd.command_name == 'branch'
    
  def _command_apply_remove(self, cmd):
    assert cmd.command_name == 'remove'
    
  @classmethod
  def _command_parse(clazz, section):
    command_name = section.header_.name
    handler_name = '_command_parse_{}'.format(command_name)
    if not hasattr(clazz, handler_name):
      raise git_temp_repo_error('unknown command parse: "{}"'.format(command_name))
    handler = getattr(clazz, handler_name)
    return handler(section)

  _file = namedtuple('_file', 'filename, perm, content')
  
  _command_file = namedtuple('_command_file', 'command_name, file')
  @classmethod
  def _command_parse_file(clazz, section):
    assert section.header_.name == 'file'

    parts = string_util.split_by_white_space(section.header_.extra_text, strip = True)
    if len(parts) != 1:
      raise git_temp_repo_error('Invalid file section header: "{}"'.format(str(section.header_)))
    filename = parts[0]
    content = ''
    if section.has_key('content'):
      content = section.get_value('content')
    perm = 0o644
    if section.has_key('perm'):
      perm = file_mode.parse_mode(section.get_value('perm'))
    f = clazz._file(filename, perm, content)
    return clazz._command_file('file', f)

  _command_add = namedtuple('_command_add', 'command_name, name, files, commit_alias, message')
  @classmethod
  def _command_parse_add(clazz, section):
    assert section.header_.name == 'add'

    parts = string_util.split_by_white_space(section.header_.extra_text, strip = True)
    if len(parts) != 2:
      raise git_temp_repo_error('Invalid "add" section header: "{}"'.format(str(section.header_)))
    commit_alias = parts[0]
    name = parts[1]

    files = []
    for entry in section:
      message = ''
      if entry.value.key == 'message':
        message = entry.value.value
      else:
        perm = 0o644
        filename = entry.value.key
        content = entry.value.value or ''
        for annotation in entry.annotations or []:
          if annotation.key == 'perm':
            perm = file_mode.parse_mode(annotation.value)
        files.append(clazz._file(filename, perm, content))
    return clazz._command_add('add', name, files, commit_alias, message)

  _command_tag = namedtuple('_command_tag', 'command_name, name, tag_name, from_commit, annotation')
  @classmethod
  def _command_parse_tag(clazz, section):
    assert section.header_.name == 'tag'

    parts = string_util.split_by_white_space(section.header_.extra_text, strip = True)
    if len(parts) != 2:
      raise git_temp_repo_error('Invalid "tag" section header: "{}"'.format(str(section.header_)))
    tag_name = parts[0]
    name = parts[1]

    from_commit = None
    annotation = None
    if section.has_key('from_commit'):
      from_commit = section.get_value('from_commit')
    if section.has_key('annotation'):
      annotation = section.get_value('annotation')

    if not from_commit:
      raise git_temp_repo_error('"tag" missing "from_commit"')
      
    return clazz._command_tag('tag', name, tag_name, from_commit, annotation)
    
  _command_branch = namedtuple('_command_branch', 'command_name, name, branch_name, from_commit, from_branch')
  @classmethod
  def _command_parse_branch(clazz, section):
    assert section.header_.name == 'branch'

    parts = string_util.split_by_white_space(section.header_.extra_text, strip = True)
    if len(parts) != 2:
      raise git_temp_repo_error('Invalid "branch" section header: "{}"'.format(str(section.header_)))
    branch_name = parts[0]
    name = parts[1]

    from_commit = None
    from_branch = None
    if section.has_key('from_commit'):
      from_commit = section.get_value('from_commit')
    if section.has_key('from_branch'):
      from_branch = section.get_value('from_branch')

    if not from_commit and not from_branch:
      raise git_temp_repo_error('"branch" missing one of "from_commit" or "from_branch"')

    if from_commit and from_branch:
      raise git_temp_repo_error('"branch" should have only one of "from_commit" or "from_branch"')
    
    return clazz._command_branch('branch', name, branch_name, from_commit, from_branch)

  _command_remove = namedtuple('_command_remove', 'command_name, name, filename')
  @classmethod
  def _command_parse_remove(clazz, section):
    assert section.header_.name == 'remove'

    parts = string_util.split_by_white_space(section.header_.extra_text, strip = True)
    if len(parts) != 1:
      raise git_temp_repo_error('Invalid "remove" section header: "{}"'.format(str(section.header_)))
    name = parts[0]

    filename = None
    if section.has_key('filename'):
      filename = section.get_value('filename')

    if not filename:
      raise git_temp_repo_error('"remove" missing one of "filename"')
    
    return clazz._command_remove('remove', name, filename)
