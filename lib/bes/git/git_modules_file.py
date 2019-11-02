#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import re

from bes.common.check import check
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
  
check.register_class(git_module)

class git_modules_file(namedtuple('git_modules_file', 'filename, modules')):

  def __new__(clazz, filename, modules):
    check.check_string(filename)
    check.check_git_module_seq(modules, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, filename, modules)

  def __str__(self):
    buf = StringIO()
    for mod in self.modules:
      print('mod: {}'.format(mod))
      buf.write(str(mod))
    return buf.getvalue()
  
  @classmethod
  def parse_file(clazz, filename):
    text = file_util.read(filename)
    return clazz.parse_text(filename, text)
    
  @classmethod
  def parse_text(clazz, filename, text):
    root = tree_text_parser.parse(text, strip_comments = True)
    modules = []
    for child in root.children:
      mod = clazz._parse_module(child)
      modules.append(mod)
    return git_modules_file(filename, modules)

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
  
'''
[submodule "ego-app"]
	path = ego-app
	url = git@bitbucket.org:imvu/ego-app.git
[submodule "ego-app-builder"]
	path = ego-app-builder
	url = git@bitbucket.org:imvu/ego-app-builder.git
'''    
