#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import re
from collections import namedtuple

from bes.common.check import check
from .git_error import git_error
from .git import git

class git_remote(namedtuple('git_remote', 'scheme, service, owner, project')):
  'Class to deal with git remote "urls"'

  _SSH_PATTERN = r'^(git)\@(.+)\:(.+)\/(.+)$'
  _HTTP_PATTERN = r'^(https?)\:\/\/(.+)\/(.+)\/(.+)$'

  def __new__(clazz, scheme, service, owner, project):
    check.check_string(scheme)
    check.check_string(service, allow_none = True)
    check.check_string(owner, allow_none = True)
    check.check_string(project)
    
    return clazz.__bases__[0].__new__(clazz, scheme, service, owner, project)
  
  def d__str__(self):
    if self.scheme == 'ssh':
      scheme = 'git'
    else:
      scheme = self.scheme
    return f'{scheme}@{self.service}:{self.owner}/{self.project}'
  
  def d__repr__(self):
    return str(self)
  
  @classmethod
  def parse(clazz, remote):
    'Parse a bitbucket remote "url" and return the parsed parts.'
    if path.isdir(remote):
      if git.is_repo(remote):
        return git_remote('local', None, None, remote)
      elif git.is_bare_repo(remote):
        return git_remote('bare_local', None, None, remote)
      else:
        raise git_error('Not a git repo: "{}"'.format(remote))

    found = clazz._find_match(remote)
    if not found:
      raise git_error('Not a valid git remote: "{}"'.format(remote))
    scheme = found[0]
    if scheme == 'git':
      scheme = 'ssh'
    service = found[1]
    owner = found[2]
    project = found[3]
    return git_remote(scheme, service, owner, project)

  @classmethod
  def _find_match(clazz, remote):
    for pattern in [ clazz._SSH_PATTERN, clazz._HTTP_PATTERN ]:
      found = re.findall(pattern, remote)
      if found:
        assert len(found) == 1
        assert len(found[0]) == 4
        return found[0]
    return None
