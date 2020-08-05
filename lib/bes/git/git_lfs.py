# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .git_exe import git_exe
from .git_lfs_entry import git_lfs_entry

class git_lfs(object):
  'A class to deal with git lfs.'

  @classmethod
  def lfs_files(clazz, root_dir):
    'Return a list of all the lfs files in the repo.'
    check.check_stirng(check)
    
    rv = git_exe.call_git(root_dir, [ 'lfs', 'ls-files', '--long' ])
    lines = git_exe.parse_lines(rv.stdout)
    entries = [ git_lfs_entry.parse_entry(line) for line in lines ]
    return sorted(entries, key = lambda entry: entry.filename)

  @classmethod
  def lfs_files_needing_smudge(clazz, root_dir):
    'Return a list of all the lfs files that need smudge.'
    files = clazz.lfs_files(root_dir)
    return [ f.filename for f in files if f.is_pointer ]

  @classmethod
  def lfs_pull(clazz, root_dir):
    args = [ 'lfs', 'pull' ]
    return git_exe.call_git(root_dir, args)

  @classmethod
  def lfs_track(clazz, root_dir, pattern):
    args = [ 'lfs', 'track', pattern ]
    return git_exe.call_git(root_dir, args)
  
  @classmethod
  def lfs_make_env(clazz, on):
    'Return a dict of the lfs env needed to clone with or without lfs smudging.'
    check.check_bool(on)
    
    return {
      'GIT_LFS_SKIP_SMUDGE': '0' if on else '1',
    }
