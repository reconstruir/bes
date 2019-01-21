#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, re
from datetime import datetime
from collections import namedtuple
from bes.text import text_line_parser
from bes.common import object_util, string_util
from bes.system import execute
from bes.fs import dir_util, file_util, temp_file
from bes.version.version_compare import version_compare

from .status import status

class git(object):
  'A class to deal with git.'

  GIT_EXE = 'git'

  branch_status_t = namedtuple('branch_status', 'ahead,behind')
  
  @classmethod
  def status(clazz, root, filenames, abspath = False):
    filenames = object_util.listify(filenames)
    flags = [ '--porcelain' ]
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
  def has_changes(clazz, root):
    return clazz.status(root, '.') != []

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
  def _call_git(clazz, root, args, raise_error = True):
    cmd = [ clazz.GIT_EXE ] + args
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
    args = [ 'checkout', 'rebision' ]
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
  def download_tarball(clazz, name, tag, address, archive_filename):
    'Download address to archive_filename.'
    archive_filename = path.abspath(archive_filename)
    tmp_dir = temp_file.make_temp_dir()
    clazz.clone(address, tmp_dir)
    flags = []
    args = [
      'archive',
      '--format=tgz',
      '--prefix=%s-%s/' % (name, tag),
      '-o',
      archive_filename,
      tag
    ]
    file_util.mkdir(path.dirname(archive_filename))
    rv = clazz._call_git(tmp_dir, args)
    file_util.remove(tmp_dir)
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
  def tag(clazz, root, tag):
    clazz._call_git(root, [ 'tag', tag ])

  @classmethod
  def push_tag(clazz, root, tag):
    clazz._call_git(root, [ 'push', 'origin', tag ])

  @classmethod
  def list_tags(clazz, root, lexical = False, reverse = False):
    if lexical:
      sort_arg = '--sort={reverse}refname'.format(reverse = '-' if reverse else '')
    else:
      sort_arg = '--sort={reverse}version:refname'.format(reverse = '-' if reverse else '')
    rv = clazz._call_git(root, [ 'tag', '-l', sort_arg ])
    return clazz._split_lines(rv.stdout)
  
  @classmethod
  def last_tag(clazz, root):
    tags = clazz.list_tags(root)
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
