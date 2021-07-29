#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import re
from collections import namedtuple

from bes.common.string_util import string_util

from .git_error import git_error
from .git import git

class git_remote(object):
  'Class to deal with git remote "urls"'

  _SSH_PATTERN = r'^(git)\@(.+)\:(.+)\/(.+)\.git$'
  _HTTP_PATTERN = r'^(https?)\:\/\/(.+)\/(.+)\/(.+)$'
  
  _parsed_remote = namedtuple('_parsed_remote', 'scheme, service, owner, project')
  @classmethod
  def parse(clazz, remote):
    'Parse a bitbucket remote "url" and return the parsed parts.'
    if path.isdir(remote):
      if git.is_repo(remote):
        return clazz._parsed_remote('local', None, None, remote)
      elif git.is_bare_repo(remote):
        return clazz._parsed_remote('bare_local', None, None, remote)
      else:
        raise git_error('Not a git repo: "{}"'.format(remote))

    found = clazz._find_match(remote)
    if not found:
      raise git_error('Not a valid git remote: "{}"'.format(remote))
    scheme = found[0]
    service = found[1]
    owner = found[2]
    project = string_util.remove_tail(found[3], '.git')
    return clazz._parsed_remote(scheme, service, owner, project)

  @classmethod
  def _find_match(clazz, remote):
    for pattern in [ clazz._SSH_PATTERN, clazz._HTTP_PATTERN ]:
      found = re.findall(pattern, remote)
      if found:
        assert len(found) == 1
        assert len(found[0]) == 4
        return found[0]
    return None
