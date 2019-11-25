#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, re, pprint, time
from datetime import datetime
from collections import namedtuple

from bes.archive.archiver import archiver
from bes.common.check import check
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.fs.dir_util import dir_util
from bes.fs.file_copy import file_copy
from bes.fs.file_ignore import file_ignore
from bes.fs.file_ignore import ignore_file_data
from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.command_line import command_line
from bes.system.compat import compat
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.text.text_line_parser import text_line_parser
from bes.version.software_version import software_version

from .git_branch import git_branch, git_branch_status
from .git_branch_list import git_branch_list
from .git_clone_options import git_clone_options
from .git_status import git_status
from .git_submodule_info import git_submodule_info

class git(object):
  'A class to deal with git.'

  log = logger('git')

  @classmethod
  def tag(clazz, root_dir, tag, allow_downgrade = False, push = False):
    greatest_tag = git.greatest_local_tag(root_dir)
    if greatest_tag and not allow_downgrade:
      if software_version.compare(greatest_tag, tag) >= 0:
        raise ValueError('new tag \"%s\" is older than \"%s\".  Use allow_downgrade to force it.' % (tag, greatest_tag))
    clazz.call_git(root_dir, [ 'tag', tag ])
    if push:
      clazz.push_tag(root_dir, tag)

  @classmethod
  def push_tag(clazz, root, tag):
    clazz.call_git(root, [ 'push', 'origin', tag ])

  @classmethod
  def delete_local_tag(clazz, root, tag):
    clazz.call_git(root, [ 'tag', '--delete', tag ])

  @classmethod
  def delete_remote_tag(clazz, root, tag):
    clazz.call_git(root, [ 'push', '--delete', 'origin', tag ])

  @classmethod
  def delete_tag(clazz, root, tag, where, dry_run):
    clazz.check_where(where)
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
    rv = clazz.call_git(root, [ 'tag', '-l', sort_arg ])
    return clazz.parse_output_lines(rv.stdout)
  
  @classmethod
  def greatest_local_tag(clazz, root):
    tags = clazz.list_local_tags(root)
    if not tags:
      return None
    return tags[-1]

  @classmethod
  def list_remote_tags(clazz, root, lexical = False, reverse = False):
    rv = clazz.call_git(root, [ 'ls-remote', '--tags' ])
    lines = clazz.parse_output_lines(rv.stdout)
    tags = [ clazz._parse_remote_tag_line(line) for line in lines ]
    if lexical:
      return sorted(tags, reverse = reverse)
    else:
      return software_version.sort_versions(tags, reverse = reverse)
    return tags

  @classmethod
  def greatest_remote_tag(clazz, root):
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
    
  _bump_tag_result = namedtuple('_bump_tag_result', 'old_tag, new_tag')
  @classmethod
  def bump_tag(clazz, root_dir, component, push = True, dry_run = False, default_tag = None, reset_lower = False):
    old_tag = git.greatest_local_tag(root_dir)
    if old_tag:
      new_tag = software_version.bump_version(old_tag, component, reset_lower = reset_lower)
    else:
      new_tag = default_tag or '1.0.0'
    if not dry_run:
      git.tag(root_dir, new_tag)
      if push:
        git.push_tag(root_dir, new_tag)
    return clazz._bump_tag_result(old_tag, new_tag)
  
  @classmethod
  def has_remote_tag(clazz, root, tag):
    return tag in clazz.list_remote_tags(root)

  @classmethod
  def has_local_tag(clazz, root, tag):
    return tag in clazz.list_local_tags(root)
