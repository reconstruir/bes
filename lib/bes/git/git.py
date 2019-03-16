#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os, os.path as path, re
from datetime import datetime
from collections import namedtuple
from bes.text import text_line_parser
from bes.common import object_util, string_util
from bes.system import execute, logger
from bes.fs import dir_util, file_ignore, file_util, tar_util, temp_file
from bes.fs.file_ignore import ignore_file_data
from bes.version.version_compare import version_compare

from .status import status

class git(object):
  'A class to deal with git.'

  _LOG = logger('git')
  
  GIT_EXE = 'git'

  branch_status_t = namedtuple('branch_status', 'ahead,behind')

  @classmethod
  def status(clazz, root, filenames, abspath = False, untracked_files = True):
    filenames = object_util.listify(filenames)
    flags = [ '--porcelain' ]
    if untracked_files:
      flags.append('--untracked-files=normal')
    else:
      flags.append('--untracked-files=no')
    args = [ 'status' ] + flags + filenames
    rv = clazz._call_git(root, args)
    result = status.parse(rv.stdout)
    if abspath:
      for r in result:
        r.filename = path.join(root, r.filename)
    return result

  @classmethod
  def branch_status(clazz, root):
    rv = clazz._call_git(root, [ 'status', '-b', '--porcelain' ])
    ahead, behind = clazz._parse_branch_status_output(root, rv.stdout)
    return clazz.branch_status_t(ahead, behind)

  @classmethod
  def remote_update(clazz, root):
    return clazz._call_git(root, [ 'remote', 'update' ])

  @classmethod
  def remote_origin_url(clazz, root):
    rv = clazz._call_git(root, [ 'remote', 'get-url', '--push', 'origin' ])
    return rv.stdout.strip()

  @classmethod
  def _parse_branch_status_output(clazz, root, s):
    lines = clazz._split_lines(s)
    ahead = re.findall('.*\[ahead\s+(\d+).*', lines[0])
    if ahead:
      ahead = int(ahead[0])
    behind = re.findall('.*behind\s+(\d+).*', lines[0])
    if behind:
      behind = int(behind[0])
    return ( ahead or 0, behind or 0 )
    
  @classmethod
  def has_changes(clazz, root, untracked_files = False):
    return clazz.status(root, '.', untracked_files = untracked_files) != []

  @classmethod
  def add(clazz, root, filenames):
    filenames = object_util.listify(filenames)
    flags = []
    args = [ 'add' ] + flags + filenames
    return clazz._call_git(root, args)

  @classmethod
  def move(clazz, root, src, dst):
    args = [ 'mv', src, dst ]
    return clazz._call_git(root, args)

  @classmethod
  def init(clazz, root, *args):
    args = [ 'init', '.' ] + list(args or [])
    return clazz._call_git(root, args)

  @classmethod
  def is_repo(clazz, root):
    expected_files = [ 'HEAD', 'config', 'index', 'refs', 'objects' ]
    for f in expected_files:
      if not path.exists(path.join(root, '.git', f)):
        return False
    return True

  @classmethod
  def check_is_git_repo(clazz, d):
    if not clazz.is_repo(d):
      raise RuntimeError('Not a git repo: %s' % (d))
  
  @classmethod
  def _call_git(clazz, root, args, raise_error = True):
    cmd = [ clazz.GIT_EXE ] + args
    clazz._LOG.log_d('root=%s; cmd=%s' % (root, ' '.join(cmd)))
    save_raise_error = raise_error
    rv = execute.execute(cmd, cwd = root, raise_error = False)
    if rv.exit_code != 0 and save_raise_error:
      message = 'git command failed: %s in %s\n' % (' '.join(cmd), root)
      message += rv.stderr
      message += rv.stdout
      print(message)
      ex = RuntimeError(message)
      setattr(ex, 'execute_result', rv)
      raise ex
    return rv

  @classmethod
  def clone(clazz, address, dest_dir, enforce_empty_dir = True):
    if path.exists(dest_dir):
      if not path.isdir(dest_dir):
        raise RuntimeError('dest_dir %s is not a directory.' % (dest_dir))
      if enforce_empty_dir:
        if not dir_util.is_empty(dest_dir):
          raise RuntimeError('dest_dir %s is not empty.' % (dest_dir))
    else:
      file_util.mkdir(dest_dir)
    args = [ 'clone', address, dest_dir ]
    return clazz._call_git(os.getcwd(), args)

  @classmethod
  def pull(clazz, root):
    args = [ 'pull', '--verbose' ]
    return clazz._call_git(root, args)

  @classmethod
  def checkout(clazz, root, revision):
    args = [ 'checkout', revision ]
    return clazz._call_git(root, args)

  @classmethod
  def push(clazz, root, *args):
    args = [ 'push', '--verbose' ] + list(args or [])
    return clazz._call_git(root, args)

  @classmethod
  def diff(clazz, root):
    args = [ 'diff' ]
    return clazz._call_git(root, args)

  @classmethod
  def patch_apply(clazz, root, patch_file):
    args = [ 'apply', patch_file ]
    return clazz._call_git(root, args)

  @classmethod
  def patch_make(clazz, root, patch_file):
    args = [ 'diff', '--patch' ]
    rv = clazz._call_git(root, args)
    file_util.save(patch_file, content = rv.stdout)

  @classmethod
  def commit(clazz, root, message, filenames):
    filenames = object_util.listify(filenames)
    message_filename = temp_file.make_temp_file(content = message)
    args = [ 'commit', '-F', message_filename ] + filenames
    return clazz._call_git(root, args)

  @classmethod
  def clone_or_pull(clazz, address, dest_dir, enforce_empty_dir = True):
    if clazz.is_repo(dest_dir):
      if clazz.has_changes(dest_dir):
        raise RuntimeError('dest_dir %s has changes.' % (dest_dir))
      return clazz.pull(dest_dir)
    else:
      return clazz.clone(address, dest_dir, enforce_empty_dir = enforce_empty_dir)

  @classmethod
  def archive(clazz, address, revision, base_name, archive_filename, untracked = False):
    'git archive with additional support to include untracked files for local repos.'
    tmp_repo_dir = temp_file.make_temp_dir()
    if path.isdir(address):
      tar_util.copy_tree_with_tar(address, tmp_repo_dir, excludes = clazz.read_gitignore(address))
      if untracked:
        clazz._call_git(tmp_repo_dir, [ 'add', '-A' ])
        clazz._call_git(tmp_repo_dir, [ 'commit', '-m', 'add untracked files just for tmp repo' ])
    else:
      if untracked:
        raise RuntimeError('untracked can only be True for local repos.')
      clazz.clone(address, tmp_repo_dir)
    archive_filename = path.abspath(archive_filename)
    file_util.mkdir(path.dirname(archive_filename))
    flags = []
    args = [
      'archive',
      '--format=tgz',
      '--prefix=%s-%s/' % (base_name, revision),
      '-o',
      archive_filename,
      revision
    ]
    rv = clazz._call_git(tmp_repo_dir, args)
    return rv
  
  @classmethod
  def short_hash(clazz, root, long_hash):
    args = [ 'rev-parse', '--short', long_hash ]
    rv = clazz._call_git(root, args)
    return rv.stdout.strip()

  @classmethod
  def long_hash(clazz, root, short_hash):
    args = [ 'rev-parse', short_hash ]
    rv = clazz._call_git(root, args)
    return rv.stdout.strip()
  
  @classmethod
  def reset_to_revision(clazz, root, revision):
    args = [ 'reset', '--hard', revision ]
    return clazz._call_git(root, args)

  @classmethod
  def last_commit_hash(clazz, root, short_hash = False):
    args = [ 'log', '--format=%H', '-n', '1' ]
    rv = clazz._call_git(root, args)
    long_hash = rv.stdout.strip()
    if not short_hash:
      return long_hash
    return clazz.short_hash(root, long_hash)

  @classmethod
  def root(clazz, filename):
    'Return the repo root for the given filename or raise and exception if not under git control.'
    cmd = [ 'git', 'rev-parse', '--show-toplevel' ]
    if path.isdir(filename):
      cwd = filename
    else:
      cwd = path.dirname(filename)
    rv = execute.execute(cmd, cwd = cwd, raise_error = False)
    if rv.exit_code != 0:
      return None
    l = text_line_parser.parse_lines(rv.stdout)
    assert len(l) == 1
    return l[0]
  
  @classmethod
  def is_tracked(clazz, root, filename):
    'Return True if the filename is tracked by a git repo.'
    args = [ 'ls-files', '--error-unmatch', filename ]
    return clazz._call_git(root, args, raise_error = False).exit_code == 0
  
  @classmethod
  def modified_files(clazz, root):
    items = clazz.status(root, '.')
    return [ item.filename for item in items if 'M' in item.action ]

  _branch_list_item = namedtuple('_branch_list_item', 'name, active, commit')
  @classmethod
  def branch_list(clazz, root):
    rv = clazz._call_git(root, [ 'branch', '-v' ])
    return [ clazz._parse_branch_list_line(line) for line in text_line_parser.parse_lines(rv.stdout) ]

  @classmethod
  def _parse_branch_list_line(clazz, s):
    parts = string_util.split_by_white_space(s, strip = True)
    active = False
    if parts[0] == '*':
      active = True
      parts.pop(0)
    assert len(parts) > 2
    name = parts[0]
    commit = parts[1]
    return clazz._branch_list_item(name, active, commit)

  @classmethod
  def active_branch(clazz, root):
    return [ i for i in clazz.branch_list(root) if i.active ][0].name

  @classmethod
  def tag(clazz, root_dir, tag, allow_downgrade = False):
    last_tag = git.last_local_tag(root_dir)
    if last_tag and not allow_downgrade:
      if version_compare.compare(last_tag, tag) >= 0:
        raise ValueError('new tag \"%s\" is older than \"%s\".  Use allow_downgrade to force it.' % (tag, last_tag))
    clazz._call_git(root_dir, [ 'tag', tag ])

  @classmethod
  def push_tag(clazz, root, tag):
    clazz._call_git(root, [ 'push', 'origin', tag ])

  @classmethod
  def delete_local_tag(clazz, root, tag):
    clazz._call_git(root, [ 'tag', '--delete', tag ])

  @classmethod
  def delete_remote_tag(clazz, root, tag):
    clazz._call_git(root, [ 'push', '--delete', 'origin', tag ])

  @classmethod
  def delete_tag(clazz, root, tag, where, dry_run):
    assert where in [ 'local', 'remote', 'both' ]
    if where in [ 'local', 'both' ]:
      local_tags = git.list_local_tags(root)
      if tag in local_tags:
        if dry_run:
          print('would delete local tag \"{tag}\"'.format(tag = tag))
        else:
          clazz.delete_local_tag(root, tag)
    if where in [ 'remote', 'both' ]:
      remote_tags = git.list_remote_tags(root)
      if tag in remote_tags:
        if dry_run:
          print('would delete remote tag \"{tag}\"'.format(tag = tag))
        else:
          clazz.delete_remote_tag(root, tag)

  @classmethod
  def list_local_tags(clazz, root, lexical = False, reverse = False):
    if lexical:
      sort_arg = '--sort={reverse}refname'.format(reverse = '-' if reverse else '')
    else:
      sort_arg = '--sort={reverse}version:refname'.format(reverse = '-' if reverse else '')
    rv = clazz._call_git(root, [ 'tag', '-l', sort_arg ])
    return clazz._split_lines(rv.stdout)
  
  @classmethod
  def last_local_tag(clazz, root):
    tags = clazz.list_local_tags(root)
    if not tags:
      return None
    return tags[-1]

  @classmethod
  def list_remote_tags(clazz, root, lexical = False, reverse = False):
    rv = clazz._call_git(root, [ 'ls-remote', '--tags' ])
    lines = clazz._split_lines(rv.stdout)
    tags = [ clazz._parse_remote_tag_line(line) for line in lines ]
    if lexical:
      return sorted(tags, reverse = reverse)
    else:
      return version_compare.sort_versions(tags, reverse = reverse)
    return tags

  @classmethod
  def last_remote_tag(clazz, root):
    tags = clazz.list_remote_tags(root)
    if not tags:
      return None
    return tags[-1]

  @classmethod
  def _parse_remote_tag_line(clazz, s):
    f = re.findall('^[0-9a-f]{40}\s+refs/tags/(.+)$', s)
    if f and len(f) == 1:
      return f[0]
    return None

  @classmethod
  def _split_lines(clazz, s):
    return [ line.strip() for line in s.split('\n') if line.strip() ]

  @classmethod
  def commit_timestamp(clazz, root, commit):
    rv = clazz._call_git(root, [ 'show', '-s', '--format=%ct', commit ])
    ts = float(rv.stdout.strip())
    return datetime.fromtimestamp(ts)

  @classmethod
  def commit_for_tag(clazz, root, tag, short_hash = False):
    args = [ 'rev-list', '-n', '1', tag ]
    rv = clazz._call_git(root, args)
    long_hash = rv.stdout.strip()
    if not short_hash:
      return long_hash
    return clazz.short_hash(root, long_hash)

  @classmethod
  def read_gitignore(clazz, root):
    'Return the contents of .gitignore with comments stripped.'
    p = path.join(root, '.gitignore')
    if not path.isfile(p):
      return None
    return ignore_file_data.read_file(p).patterns

  @classmethod
  def config_set_value(clazz, key, value):
    clazz._call_git('/tmp', [ 'config', '--global', key, value ], raise_error = False)
    
  @classmethod
  def config_unset_value(clazz, key):
    clazz._call_git('/tmp', [ 'config', '--global', '--unset', key ], raise_error = False)
    
  @classmethod
  def config_get_value(clazz, key):
    rv = clazz._call_git('/tmp', [ 'config', '--global', key ], raise_error = False)
    if rv.exit_code == 0:
      return string_util.unquote(rv.stdout.strip())
    else:
      return None
  
  @classmethod
  def config_set_identity(clazz, name, email):
    clazz._call_git('/tmp', [ 'config', '--global', 'user.name', '"%s"' % (name) ])
    clazz._call_git('/tmp', [ 'config', '--global', 'user.email', '"%s"' % (email) ])

  _identity = namedtuple('_identity', 'name, email')
  @classmethod
  def config_get_identity(clazz):
    return clazz._identity(clazz.config_get_value('user.name'),
                           clazz.config_get_value('user.email'))
    
  _bump_tag_result = namedtuple('_bump_tag_result', 'old_tag, new_tag')
  @classmethod
  def bump_tag(clazz, root_dir, component = None, push = True, dry_run = False, default_tag = None):
    old_tag = git.last_local_tag(root_dir)
    if old_tag:
      new_tag = version_compare.bump_version(old_tag, component = component, delimiter = '.')
    else:
      new_tag = default_tag or '1.0.0'
    if not dry_run:
      git.tag(root_dir, new_tag)
      if push:
        git.push_tag(root_dir, new_tag)
    return clazz._bump_tag_result(old_tag, new_tag)
