#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import re

from bes.common.check import check
from bes.common.tuple_util import tuple_util
from bes.compat.StringIO import StringIO
from bes.fs.file_util import file_util
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.text.tree_text_parser import tree_text_parser

class git_module(namedtuple('git_module', 'name, path, url, branch')):

  def __new__(clazz, name, path, url, branch):
    check.check_string(name)
    check.check_string(path)
    check.check_string(url)
    check.check_string(branch, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, name, path, url, branch)

  def __str__(self):
    buf = StringIO()
    buf.write('[submodule "{}"]\n'.format(self.name))
    buf.write('\tpath = {}\n'.format(self.path))
    buf.write('\turl = {}\n'.format(self.url))
    if self.branch:
      buf.write('\tbranch = {}\n'.format(self.branch))
    return buf.getvalue()

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
check.register_class(git_module)

class git_modules_file(object):

  def __init__(self, filename):
    check.check_string(filename)
    self._filename = filename
    self._modules = self._parse_file(filename)

  def set_branch(self, name, branch):
    check.check_string(name)
    check.check_string(branch, allow_none = True)
    for i, mod in enumerate(self._modules):
      if mod.name == name:
        if mod.branch != branch:
          self._modules[i] = mod.clone(mutations = { 'branch': branch })
          self.save()
        return
    raise KeyError('modules not found: {}'.format(name))
        
  def save(self):
    new_content = str(self)
    old_content = file_util.read(self._filename)
    if new_content != old_content:
      file_util.save(self._filename, new_content)
        
  def __str__(self):
    buf = StringIO()
    for mod in self._modules:
      buf.write(str(mod))
    return buf.getvalue()
  
  @classmethod
  def _parse_file(clazz, filename):
    text = file_util.read(filename)
    return clazz._parse_text(filename, text)
    
  @classmethod
  def _parse_text(clazz, filename, text):
    root = tree_text_parser.parse(text, strip_comments = True)
    modules = []
    for child in root.children:
      mod = clazz._parse_module(child)
      modules.append(mod)
    return modules

  @classmethod
  def _parse_module(clazz, node):
    name = clazz._parse_entry_header(node.data.text)
    if not name:
      raise RuntimeError('Invalid module header: "{}"'.format(node.data.text))
    values = key_value_list()
    for child in node.children:
      kv = key_value.parse(child.data.text)
      values.append(kv)
    d = values.to_dict()
    mpath = d.get('path', None)
    url = d.get('url', None)
    branch = d.get('branch', None)
    return git_module(name, mpath, url, branch)
    
  _ENTRY_HEADER_PATTERN = '\[submodule\s+\"(.+)\"\]'
  @classmethod
  def _parse_entry_header(clazz, text):
    f = re.findall(clazz._ENTRY_HEADER_PATTERN, text)
    if f and len(f) == 1:
      return f[0]
    return None
