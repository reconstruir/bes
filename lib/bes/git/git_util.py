#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_type, file_util
from bes.fs.find import finder, criteria, file_type_criteria, max_depth_criteria, pattern_criteria
from bes.compat import StringIO
from bes.common import string_util

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

  def _command_bump_tag(self, tag, root_dir, part, dry_run, push):
    last_tag = git.last_tag(root_dir)
    if tag:
      new_tag = tag
    else:
      if part == 'minor':
        deltas = [ 0, 1, 0 ]
      if not last_tag:
        new_tag = '1.0.0'
      else:
        new_tag = version_compare.change_version(last_tag, self._DELTA_MAP[part])
    print('last_tag: %s' % (last_tag))
    print(' new_tag: %s' % (new_tag))
    if last_tag:
      if version_compare.compare(last_tag, new_tag) >= 0:
        print('new_tag \"%s\" is older than \"%s\"' % (new_tag, last_tag))
        return 1
    if dry_run:
      return
    git.tag(root_dir, new_tag)
    if push:
      git.push_tag(root_dir, new_tag)
    return 0
  
