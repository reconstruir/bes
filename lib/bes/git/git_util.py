#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.compat.StringIO import StringIO
from bes.fs.file_find import file_find
from bes.fs.file_type import file_type
from bes.fs.file_util import file_util
from bes.fs.find.criteria import criteria
from bes.fs.find.file_type_criteria import file_type_criteria
from bes.fs.find.finder import finder
from bes.fs.find.max_depth_criteria import max_depth_criteria
from bes.fs.find.pattern_criteria import pattern_criteria
from bes.fs.temp_file import temp_file
from bes.system.execute import execute

from .git import git
from .git_repo import git_repo
from .git_repo_script_options import git_repo_script_options

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
    address = git.resolve_address(address)
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
    'Return True if h is a long hash.'
    return git.is_long_hash(h)

  @classmethod
  def is_short_hash(clazz, h):
    'Return True if h is a short hash.'
    return git.is_short_hash(h)

  @classmethod
  def repo_greatest_tag(clazz, address):
    'Return the greatest numeric tag of a git project by address.'
    tmp_dir, repo = clazz._clone_to_temp_dir(address)
    greatest_tag = repo.greatest_local_tag()
    file_util.remove(tmp_dir)
    return greatest_tag

  @classmethod
  def repo_bump_tag(clazz, address, component, dry_run, reset_lower = False):
    'Bump the tag of a repo by address.'
    tmp_dir, repo = clazz._clone_to_temp_dir(address)
    result = repo.bump_tag(component, push = True, dry_run = dry_run, reset_lower = reset_lower)
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
  def repo_run_script(clazz, address, script, args, options = None):
    scripts = [ clazz.script(script, args or []) ]
    results = clazz.repo_run_scripts(address, scripts, options = options)
    return results[0]
                
  script = namedtuple('script', 'filename, args')
  @classmethod
  def repo_run_scripts(clazz, address, scripts, options = None):
    check.check_git_repo_script_options(options, allow_none = True)
    options = options or git_repo_script_options()
    tmp_dir, repo = clazz._clone_to_temp_dir(address)
    results = []
    for script in scripts:
      if not repo.has_file(script.filename):
        raise IOError('script not found in {}/{}'.format(address, script.filename))
      if options.dry_run:
        print('DRY_RUN: would run {}/{} {} push={}'.format(address, script.filename, script.args or '', options.push))
        results.append(None)
      else:
        cmd = [ script.filename ]
        if script.args:
          cmd.extend(script.args)
        rv = execute.execute(cmd, cwd = repo.root, shell = True)
        results.append(rv)
    if options.push:
      if options.dry_run:
        print('DRY_RUN: {}: would push'.format(address))
      else:
        repo.push()
    if options.bump_tag_component is not None:
      if options.dry_run:
        rv = repo.bump_tag(options.bump_tag_component, dry_run = True)
        print('DRY_RUN: {}: would bump "{}" component of tag {} to {}'.format(address, options.bump_tag_component, rv.old_tag, rv.new_tag))
      else:
        repo.bump_tag(options.bump_tag_component, push = True)
    return results
  
  @classmethod
  def find_root_dir(clazz, start_dir = None):
    'Find the root of a git repo starting at start_dir or None if not found.'
    start_dir = start_dir or os.getcwd()
    return file_find.find_in_ancestors(start_dir, '.git')
  
