#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from bes.fs import file_find, file_type, file_util, temp_file
from bes.fs.find import finder, criteria, file_type_criteria, max_depth_criteria, pattern_criteria
from bes.compat import StringIO
from bes.common import string_util
from bes.system import execute

from .git_repo import git_repo

class git_util(object):
  'git util.'

  @classmethod
  def find_git_dirs(clazz, dirs):
    'Return the first .git dir found in any dir in dirs.'
    dirs = [ d for d in dirs if path.isdir(d) ]
    possible = []
    result = clazz._find(dirs, '.git', None, None, False)
    result = [ file_util.remove_tail(d, '.git') for d in result ]
    return sorted(result)

  @classmethod
  def _find(clazz, files, name, ft, max_depth, quit):
    if ft:
      ft = file_type.validate_file_type(ft)
    for f in files:
      if path.isdir(f):
        ff = clazz._make_finder(f, name, ft, max_depth, quit)
        for f in ff.find():
          yield f
  
  @classmethod
  def _make_finder(clazz, d, name, ft, max_depth, quit):
    crit_list = []
    if max_depth:
      crit_list.append(max_depth_criteria(max_depth))
    if name:
      if quit:
        action = criteria.STOP
      else:
        action = criteria.FILTER
      crit_list.append(pattern_criteria(name, action = action))
    if ft:
      crit_list.append(file_type_criteria(ft))
    return finder(d, criteria = crit_list)

  @classmethod
  def name_from_address(clazz, address):
    if path.isdir(address):
      return path.basename(address)
    if not address.endswith('.git'):
      raise ValueError('not a git address: %s' % (address))
    buf = StringIO()
    for c in string_util.reverse(address):
      if c in ':/':
        break
      buf.write(c)
    last_part = string_util.reverse(buf.getvalue())
    return string_util.remove_tail(last_part, '.git')

  @classmethod
  def sanitize_address(clazz, address):
    'Return path for local tarball.'
    return string_util.replace(address, { ':': '_', '/': '_' })
  
  @classmethod
  def is_long_hash(clazz, h):
    'Return True if h is a long hash.  Only checks length not string validity.'
    return len(h) == 40

  @classmethod
  def is_short_hash(clazz, h):
    'Return True if h is a short hash.  Only checks length not string validity.'
    return len(h) == 7

  @classmethod
  def repo_greatest_tag(clazz, address):
    'Return the greatest numeric tag of a git project by address.'
    tmp_dir, repo = clazz._clone_to_temp_dir(address)
    greatest_tag = repo.greatest_local_tag()
    file_util.remove(tmp_dir)
    return greatest_tag

  @classmethod
  def repo_bump_tag(clazz, address, component, dry_run):
    'Bump the tag of a repo by address.'
    tmp_dir, repo = clazz._clone_to_temp_dir(address)
    result = repo.bump_tag(component = component, push = True, dry_run = dry_run)
    file_util.remove(tmp_dir)
    return result
  
  @classmethod
  def _clone_to_temp_dir(clazz, address):
    'Clone a git address to a temp dir'
    tmp_dir = temp_file.make_temp_dir()
    r = git_repo(tmp_dir, address = address)
    r.clone()
    return tmp_dir, r
  
  @classmethod
  def repo_run_script(clazz, address, script, args, push, dry_run):
    tmp_dir, repo = clazz._clone_to_temp_dir(address)
    if not repo.has_file(script):
      raise IOError('script not found in {}/{}'.format(address, script))
    if dry_run:
      print('would run {}/{} {} push={}'.format(address, script, args or '', push))
      return None
    cmd = [ script ]
    if args:
      cmd.extend(args)
    rv = execute.execute(cmd, cwd = repo.root)
    if push:
      repo.push()
    return rv

  @classmethod
  def find_root_dir(clazz, start_dir = None):
    'Find the root of a git repo starting at start_dir or None if not found.'
    start_dir = start_dir or os.getcwd()
    return file_find.find_in_ancestors(start_dir, '.git')
  
