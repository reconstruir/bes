#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, re
from collections import namedtuple
from bes.text import lines
from bes.common import object_util, Shell, string_util
from bes.fs import dir_util, file_util, temp_file
from bes.fs import dir_util, file_util, temp_file

from .status import status

class git(object):
  'A class to deal with git.'

  GIT_EXE = 'git'

  branch_status_t = namedtuple('branch_status', 'ahead,behind')
  
  @classmethod
  def status(clazz, root, filenames):
    filenames = object_util.listify(filenames)
    flags = [ '--porcelain' ]
    args = [ 'status' ] + flags + filenames
    rv = clazz._call_git(root, args)
    return status.parse(rv.stdout)

  @classmethod
  def branch_status(clazz, root):
    rv = clazz._call_git(root, [ 'status', '-b', '--porcelain' ])
    ahead, behind = clazz._parse_branch_status_output(root, rv.stdout)
    return clazz.branch_status_t(ahead, behind)

  @classmethod
  def remote_update(clazz, root):
    return clazz._call_git(root, [ 'remote', 'update' ])

  @classmethod
  def _parse_branch_status_output(clazz, root, s):
    lines = [ line.strip() for line in s.split('\n') ]
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
  def init(clazz, root):
    args = [ 'init', '.' ]
    return clazz._call_git(root, args)

  @classmethod
  def is_repo(clazz, root):
    expected_files = [ 'HEAD', 'config', 'index', 'refs', 'objects' ]
    for f in expected_files:
      if not path.exists(path.join(root, '.git', f)):
        return False
    return True

  @classmethod
  def _call_git(clazz, root, args):
    cmd = [ clazz.GIT_EXE ] + args
    rv = Shell.execute(cmd, cwd = root)
    #print(cmd)
    #print(rv.stdout)
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
  def push(clazz, root):
    args = [ 'push', '--verbose' ]
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
    cwd = path.dirname(filename)
    rv = Shell.execute(cmd, cwd = cwd)
    l = lines.parse_lines(rv.stdout)
    assert len(l) == 1
    return l[0]
  
  @classmethod
  def modified_files(clazz, root):
    items = clazz.status(root, '.')
    return [ item.filename for item in items if 'M' in item.action ]
