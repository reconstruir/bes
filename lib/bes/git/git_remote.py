#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple

class git_remote(object):
  'Class to deal with git remote "urls"'

  _SSH_PATTERN = '^git\@(.+)\:(.+)\/(.+)\.git$'
  _HTTP_PATTERN = '^http\:\/\/(.+)\/(.+)\/(.+)$'
  
  _parsed_remote = namedtuple('_parsed_remote', 'scheme, service, owner, project')
  @classmethod
  def parse(clazz, remote):
    'Parse a bitbucket remote "url" and return the parsed parts.'
    found = re.findall(clazz._SSH_PATTERN, remote)
    scheme = None
    if found:
      scheme = 'ssh'
    else:
      found = re.findall(clazz._HTTP_PATTERN, remote)
      if found:
        scheme = 'http'
    if not scheme:
      raise ValueError('Not a valid ssh or http remote: "{}"'.format(remote))
    if len(found) != 1:
      raise ValueError('Not a valid ssh or http remote: "{}"'.format(remote))
    if len(found[0]) != 3:
      raise ValueError('Not a valid ssh or http remote: "{}"'.format(remote))
    service = found[0][0]
    owner = found[0][1]
    project = found[0][2]
    return clazz._parsed_remote(scheme, service, owner, project)
