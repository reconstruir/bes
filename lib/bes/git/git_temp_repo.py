#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect
from collections import namedtuple

from ..system.check import check
from bes.common.string_util import string_util
from bes.fs.temp_file import temp_file
from bes.fs.file_mode import file_mode
from bes.config.simple_config import simple_config
from bes.config.simple_config_options import simple_config_options

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
               prefix = None, commit_message = None, config = None,
               where = None):
    self._debug = debug
    if remote:
      self._init_remote(content, prefix, commit_message = commit_message, where = where)
    else:
      self._init_local(content, prefix, commit_message = commit_message, where = None)
    if config:
      self.apply_config_text(config)

  def _init_remote(self, content, prefix, commit_message = None, where = None):
    if prefix:
      remote_prefix = '{}remote-'.format(prefix)
    else:
      remote_prefix = 'remote-'
    self._remote_repo = self._make_temp_repo(init_args = [ '--bare', '--shared' ],
                                             debug = self._debug,
                                             prefix = remote_prefix,
                                             commit_message = commit_message,
                                             where = None)
    if prefix:
      local_prefix = '{}local-'.format(prefix)
    else:
      local_prefix = 'local-'
    tmp_dir = temp_file.make_temp_dir(delete = not self._debug, prefix = local_prefix, dir = where)
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
    
  def _init_local(self, content, prefix, commit_message = None, where = None):
    tmp_dir = temp_file.make_temp_dir(delete = not self._debug, prefix = prefix, dir = where)
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
      
  def make_temp_cloned_repo(self, prefix = None, where = None):
    tmp_dir = temp_file.make_temp_dir(delete = not self._debug, prefix = prefix, dir = where)
    if self._debug:
      print('git_temp_repo: tmp_dir: %s' % (tmp_dir))
    r = git_repo(tmp_dir, address = self._remote_repo.root)
    r.clone()
    return r
      
  @classmethod
  def _make_temp_repo(clazz, init_args = None, content = None, debug = False,
                      prefix = None, commit_message = None, suffix = None,
                      where = None):
    tmp_dir = temp_file.make_temp_dir(delete = not debug, prefix = prefix,
                                      suffix = suffix, dir = where)
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

    config_options = simple_config_options(key_check_type = simple_config_options.KEY_CHECK_ANY)
    config = simple_config.from_text(config_text,
                                     source = '<git_temp_repo>',
                                     check_env_vars = False,
                                     options = config_options)
    cmds = []
    for section in config:
      cmd = self._command_parse(section)
      cmds.append(cmd)
    context = {
      'commit_aliases': {},
      'files': {},
    }
    for cmd in cmds:
      self._command_apply(cmd, context)

  def _command_apply(self, cmd, context):
    handler_name = '_command_apply_{}'.format(cmd.command_name)
    if not hasattr(self, handler_name):
      raise git_temp_repo_error('unknown command apply: "{}"'.format(cmd.command_name))
    handler = getattr(self, handler_name)
    return handler(cmd, context)

  def _command_apply_file(self, cmd, context):
    assert cmd.command_name == 'file'
    context['files'][cmd.file.filename] = cmd.file

  def _command_apply_add(self, cmd, context):
    assert cmd.command_name == 'add'
    for f in cmd.files:
      resolved_file = self._resolve_file(f.content, context)
      if resolved_file:
        content = resolved_file.content
        mode = resolved_file.mode
      else:
        content = f.content
        mode = f.mode
      self.add_file(f.filename, content, mode = mode, commit = False)
    message = cmd.message or 'add {}'.format(' '.join([ f.filename for f in cmd.files ]))
    commit_hash = self.commit(message, [ f.filename for f in cmd.files ])
    key = '@{}'.format(cmd.commit_alias)
    if key in context['commit_aliases']:
      raise git_temp_repo_error('duplicate commit alias: "{}"'.format(cmd.commit_alias))
    context['commit_aliases'][key] = commit_hash

  def _resolve_commit(self, commit_alias, context):
    return context['commit_aliases'].get(commit_alias, commit_alias)

  def _resolve_file(self, content, context):
    if not content.startswith('@'):
      return None
    key = content[1:]
    return context['files'].get(key, None)
  
  def _command_apply_tag(self, cmd, context):
    assert cmd.command_name == 'tag'
    self.tag(cmd.tag_name, allow_downgrade = True, push = cmd.push,
             commit = cmd.from_commit, annotation = cmd.annotation)
    
  def _command_apply_branch(self, cmd, context):
    assert cmd.command_name == 'branch'
    start_point = self._resolve_commit(cmd.start_point, context)
    self.branch_create(cmd.branch_name, push = cmd.push, start_point = start_point)
    
  def _command_apply_remove(self, cmd, context):
    assert cmd.command_name == 'remove'
    self.remove(cmd.filename)

  def _command_apply_push(self, cmd, context):
    assert cmd.command_name == 'push'
    args = []
    if cmd.upstream:
      args.append('--set-upstream')
      args.append(cmd.upstream)
    args.append(cmd.repository)
    args.append(cmd.ref)
    self.push(*args)
    
  @classmethod
  def _command_parse(clazz, section):
    command_name = section.header_.name
    handler_name = '_command_parse_{}'.format(command_name)
    if not hasattr(clazz, handler_name):
      raise git_temp_repo_error('unknown command parse: "{}"'.format(command_name))
    handler = getattr(clazz, handler_name)
    return handler(section)

  _file = namedtuple('_file', 'filename, mode, content')
  
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

  _command_tag = namedtuple('_command_tag', 'command_name, name, tag_name, from_commit, annotation, push')
  @classmethod
  def _command_parse_tag(clazz, section):
    assert section.header_.name == 'tag'

    parts = string_util.split_by_white_space(section.header_.extra_text, strip = True)
    if len(parts) < 2:
      raise git_temp_repo_error('Invalid "tag" section header: "{}"'.format(str(section.header_)))
    tag_name = parts.pop(0)
    name = parts.pop(0)
    from_commit = None
    push = True
    annotation = None
    if parts:
      from_commit = parts.pop(0)
    if parts:
      annotation = ''.join(parts)
    if section.has_key('from_commit'):
      from_commit = section.get_value('from_commit')
    if section.has_key('annotation'):
      annotation = section.get_value('annotation')
    if section.has_key('push'):
      push = section.get_bool('push')

    if not from_commit:
      raise git_temp_repo_error('"tag" missing "from_commit"')
      
    return clazz._command_tag('tag', name, tag_name, from_commit, annotation, push)
    
  _command_branch = namedtuple('_command_branch', 'command_name, name, branch_name, start_point, push')
  @classmethod
  def _command_parse_branch(clazz, section):
    assert section.header_.name == 'branch'

    parts = string_util.split_by_white_space(section.header_.extra_text, strip = True)
    if len(parts) != 2:
      raise git_temp_repo_error('Invalid "branch" section header: "{}"'.format(str(section.header_)))
    branch_name = parts[0]
    name = parts[1]

    start_point = None
    push = False
    if section.has_key('start_point'):
      start_point = section.get_value('start_point')
    if section.has_key('push'):
      push = section.get_bool('push')

    return clazz._command_branch('branch', name, branch_name, start_point, push)

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

  _command_push = namedtuple('_command_push', 'command_name, repository, ref, upstream')
  @classmethod
  def _command_parse_push(clazz, section):
    assert section.header_.name == 'push'

    parts = string_util.split_by_white_space(section.header_.extra_text, strip = True)
    if len(parts) != 2:
      raise git_temp_repo_error('Invalid "push" section header: "{}"'.format(str(section.header_)))
    repository = parts.pop(0)
    ref = parts.pop(0)
    upstream = None
    if section.has_key('upstream'):
      upstream = section.get_value('upstream')
    return clazz._command_push('push', repository, ref, upstream)
  
