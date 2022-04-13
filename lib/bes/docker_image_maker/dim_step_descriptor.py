#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple

from ..system.check import check
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property

from .dim_step import dim_step
from .dim_system import dim_system
from .dim_python import dim_python
from .dim_error import dim_error

class dim_step_descriptor(namedtuple('dim_step_descriptor', 'repo_name_prefix, step_name, tag_version, system_name, system_version, python_version, address')):

  def __new__(clazz, repo_name_prefix, step_name, tag_version, system_name, system_version, python_version, address = None):
    check.check_string(repo_name_prefix)
    check.check_string(step_name)
    check.check_string(tag_version)
    check.check_string(system_name)
    check.check_string(system_version)
    check.check_string(python_version)
    check.check_string(address, allow_none = True)

    dim_step.check_step_name(step_name)
    dim_system.check_system_name(system_name)
    dim_system.check_system_version(system_name, system_version)
    dim_python.check_python_version(python_version)
    
    return clazz.__bases__[0].__new__(clazz,
                                      repo_name_prefix,
                                      step_name,
                                      tag_version,
                                      system_name,
                                      system_version,
                                      python_version,
                                      address)

  def __str__(self):
    return self.named_tag

  @classmethod
  def parse(clazz, s, has_address = False):
    if has_address:
      address, sep, right_side = s.partition('/')
      if sep != '/':
        raise dim_error('Invalid step descriptor: "{}"'.format(s))
    else:
      address = None
      right_side = s
    f = re.findall(r'^(.*)/(.*):(.*)_(.*)-(.*)_py(.*)$', right_side)
    if not f or len(f) != 1 or len(f[0]) != 6:
      raise dim_error('Invalid step descriptor: "{}"'.format(s))
    fields = list(f[0])
    repo_name_prefix = fields.pop(0)
    step_name = fields.pop(0)
    tag_version = fields.pop(0)
    system_name = fields.pop(0)
    system_version = fields.pop(0)
    python_version = fields.pop(0)
    return dim_step_descriptor(repo_name_prefix,
                               step_name,
                               tag_version,
                               system_name,
                               system_version,
                               python_version,
                               address = address)
  
  @cached_property
  def repo_name(self):
    'Return the repo_name.'
    return '{repo_name_prefix}/{step_name}'.format(**self._asdict())

  @cached_property
  def tag(self):
    'Return the tag.'
    return '{tag_version}_{system_name}-{system_version}_py{python_version}'.format(**self._asdict())
  
  @cached_property
  def named_tag(self):
    'Return the complete docker named tag.'
    return '{repo_name}:{tag}'.format(repo_name = self.repo_name,
                                      tag = self.tag)

  @cached_property
  def addressed_repo_name(self):
    'Return the addressed repo_name.'
    if not self.address:
      raise dim_error('No address given for: "{}"'.format(self.named_tag))
    return '{address}/{repo_name_prefix}/{step_name}'.format(**self._asdict())

  @cached_property
  def addressed_named_tag(self):
    'Return the complete docker named tag.'
    return '{addressed_repo_name}:{tag}'.format(addressed_repo_name = self.addressed_repo_name,
                                                tag = self.tag)
  
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
check.register_class(dim_step_descriptor)
