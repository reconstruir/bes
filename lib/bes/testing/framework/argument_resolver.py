#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch, os.path as path, random, re

from bes.common import algorithm, check, object_util
from bes.fs import file_check, file_multi_ignore, file_path, file_util
from bes.git import git
from bes.python import dependencies
from bes.system import env_var
from bes.text import text_line_parser
from bes.system import execute

from .config_env import config_env
from .file_filter import file_filter
from .file_finder import file_finder
from .file_info import file_info
from .file_info_list import file_info_list
from .unit_test_description import unit_test_description

class argument_resolver(object):

  def __init__(self, working_dir, arguments, root_dir = None, file_ignore_filename = None, check_git = False, use_env_deps = True):
    self._num_iterations = 1
    self._randomize = False
    self._raw_test_descriptions = []
    file_check.check_dir(working_dir)
    if root_dir:
      file_check.check_dir(root_dir)
    working_dir = path.abspath(working_dir)
    ignore = file_multi_ignore(file_ignore_filename)
    arguments_just_files, arguments_just_filters = self._split_files_and_filters(working_dir, arguments)
    filter_patterns = self._make_filters_patterns(arguments_just_filters)
    unresolved_files, unresolved_dirs = self._split_files_and_dirs(working_dir, arguments_just_files)
    if check_git:
      files = self._git_tracked_modified_files(unresolved_dirs + unresolved_files)
    else:
      files = self._resolve_files_and_dirs(working_dir, arguments_just_files)
    if not files:
      return
    if not root_dir:
      root_dir = self._find_root_dir(files)
      if not root_dir:
        raise RuntimeError('Failed to determine root dir.')
    self.root_dir = root_dir
    self.config_env = config_env(root_dir)
    self.all_files = ignore.filter_files(files)
    file_infos = file_info_list([ file_info(self.config_env, f) for f in self.all_files ])
    file_infos += self._tests_for_many_files(file_infos)
    file_infos.remove_dups()
    file_infos = file_infos.filter_by_filenames(filter_patterns)
    file_infos = file_infos.filter_by_test_filename_only()
    self.inspect_map = file_infos.make_inspect_map()
    # FIXME: change to ignore_without_tests()
    file_infos = file_info_list([ f for f in file_infos if f.filename in self.inspect_map ])
    # FIXME: change to filter_with_patterns_tests()
    self._raw_test_descriptions = file_filter.filter_files(file_infos, filter_patterns)
    if use_env_deps:
      self._env_dependencies = self.config_env.resolve_deps(self._config_names())
    else:
      self._env_dependencies = []
    self._env_dependencies_configs = [ self.config_env.config_for_name(name) for name in self._env_dependencies ]
      
  @property
  def num_iterations(self):
    return self._num_iterations
    
  @num_iterations.setter
  def num_iterations(self, n):
    check.check_int(n)
    if not n in range(1, 110):
      raise ValueError('Iterations needs to be between 1 and 10: %d' % (n))
    self._num_iterations = n

  @property
  def randomize(self):
    return self._randomize
    
  @randomize.setter
  def randomize(self, randomize):
    check.check_bool(randomize)
    self._randomize = randomize

  @property
  def test_descriptions(self):
    descriptions = sorted(self._raw_test_descriptions * self._num_iterations)
    if self._randomize:
      random.shuffle(descriptions)
    return descriptions
      
  @classmethod
  def _git_roots(clazz, files):
    files = object_util.listify(files)
    roots = [ git.root(f) for f in files ]
    roots = [ r for r in roots if r ]
    return algorithm.unique(roots)

  @classmethod
  def _split_files_and_filters(clazz, working_dir, arguments):
    files = []
    filter_descriptions = []
    for arg in arguments:
      normalized_path = file_path.normalize(path.join(working_dir, arg))
      if not path.exists(normalized_path):
        filter_descriptions.append(arg)
      else:
        files.append(arg)
    filters = [ unit_test_description.parse(f) for f in (filter_descriptions or []) ]
    return files, filters

  @classmethod
  def _resolve_files_and_dirs(clazz, working_dir, files_and_dirs):
    result = []
    for f in files_and_dirs:
      f = file_path.normalize(path.join(working_dir, f))
      if path.isfile(f):
        result += [ f ]
      elif path.isdir(f):
        result += clazz._resolve_dir(f)
    result = algorithm.unique(result)
    result = [ path.normpath(r) for r in result ]
    return sorted(result)

  @classmethod
  def _split_files_and_dirs(clazz, working_dir, files_and_dirs):
    files = []
    dirs = []
    for f in files_and_dirs:
      f = file_path.normalize(path.join(working_dir, f))
      if path.isfile(f):
        files += [ f ]
      elif path.isdir(f):
        dirs += [ f ]
      else:
        raise ValueError('not a file or directory: %s' % (str(f)))
    files = sorted(algorithm.unique(files))
    dirs = sorted(algorithm.unique(dirs))
    return files, dirs

  @classmethod
  def _resolve_dir(clazz, d):
    assert path.isdir(d)
    return file_finder.find_python_files(d)
    
  @classmethod
  def _resolve_file(clazz, f):
    assert path.isfile(f)
    return [ path.abspath(path.normpath(f)) ]

  def _test_for_file(self, finfo):
    if not finfo.relative_filename:
      return None
    if finfo.relative_filename.startswith('tests/'):
      return None
    name = path.splitext(path.basename(finfo.filename))[0]
    test_basename = 'test_%s.py' % (name)
    test_fragment = path.dirname(finfo.relative_filename)
    test_full_path = path.join(finfo.config.root_dir, 'tests', test_fragment, test_basename)
    if path.isfile(test_full_path):
      return file_info(self.config_env, test_full_path)
    return None

  def _tests_for_many_files(self, finfos):
    result = file_info_list()
    for finfo in finfos:
      test = self._test_for_file(finfo)
      if test:
        result.append(test)
    return result

  @classmethod
  def _resolve_tests_for_files(clazz, file_infos):
    result = []
    for f in files:
      test = clazz.test_for_file(f)
      if test:
        result.append(test)
    return result

  @classmethod
  def _find_root_dir_with_git(clazz, files):
    if not files:
      return None
    any_git_root = git.root(files[0])
    if any_git_root:
      return file_path.parent_dir(any_git_root)
    return False

  @classmethod
  def _find_root_dir_with_file_marker(clazz, files):
    common_ancestor = file_path.common_ancestor(files)
    if not common_ancestor:
      return None
    marker = file_util.find_in_ancestors(common_ancestor, '.bes_test_root')
    if not marker:
      return None
    return path.dirname(marker)

  @classmethod
  def _find_root_dir(clazz, files):
    root_dir = clazz._find_root_dir_with_file_marker(files)
    if root_dir:
      return root_dir
    root_dir = clazz._find_root_dir_with_git(files)
    if root_dir:
      return root_dir
    return None

  @classmethod
  def _make_filters_patterns(clazz, filters):
    patterns = []
    for f in filters:
      filename_pattern = None
      fixture_pattern = None
      function_pattern = None
      if f.filename:
        filename_pattern = clazz._make_fnmatch_pattern(f.filename)
      if f.fixture:
        fixture_pattern = clazz._make_fnmatch_pattern(f.fixture)
      if f.function:
        function_pattern = clazz._make_fnmatch_pattern(f.function)
      patterns.append(unit_test_description(filename_pattern, fixture_pattern, function_pattern))
    return patterns

  @classmethod
  def _make_fnmatch_pattern(clazz, pattern):
    pattern = pattern.lower()
    if clazz._is_fnmatch_pattern(pattern):
      return pattern
    return '*%s*' % (pattern)
  
  @classmethod
  def _is_fnmatch_pattern(clazz, pattern):
    for c in [ '*', '?', '[', ']', '!' ]:
      if pattern.count(c) > 0:
        return True
    return False

  def print_files(self):
    for desc in self._raw_test_descriptions:
      print(path.relpath(desc.file_info.filename))

  def print_tests(self):
    longest_file_name = max([ len(path.relpath(desc.file_info.filename)) for desc in self._raw_test_descriptions ])
    for desc in self._raw_test_descriptions:
      inspection = desc.file_info.inspection
      for i in inspection:
        filename = path.relpath(i.filename).rjust(longest_file_name)
        print('%s %s.%s' % (filename, i.fixture, i.function))
      
  def ignore_with_patterns(self, patterns):
    if patterns:
      self._raw_test_descriptions = file_filter.ignore_files(self._raw_test_descriptions, patterns)
    
  def _config_names(self):
    result = []
    for desc in self.test_descriptions:
      if desc.file_info.config:
        result.append(desc.file_info.config.data.name)
    return algorithm.unique(result)
  
  @classmethod
  def _git_tracked_modified_files(clazz, unresolved_files):
    roots = clazz._git_roots(unresolved_files)
    statuses = [ git.status(root, '.', abspath = True) for root in roots ]
    result = []
    for s in statuses:
      for x in s:
        if x.filename.lower().endswith('.py'):
          if x.action in [ 'M', 'A' ]:
            result.append(x.filename)
    return result

  def supports_test_dependency_files(self):
    return dependencies.is_supported()
  
  def test_dependency_files(self):
    result = {}
    for desc in self.test_descriptions:
      filename = desc.file_info.filename
      assert filename not in result
      result[filename] = []
      deps = dependencies.dependencies(filename)
      for d in deps:
        fi = file_info(self.config_env, d)
        result[filename].append(fi)
    return result

  @property
  def env_dependencies_configs(self):
    return self._env_dependencies_configs
  
  def update_environment(self, env, variables):
    for config in self._env_dependencies_configs:
      substituted = config.substitute(variables)
      env_var(env, 'PATH').append(substituted.data.unixpath)
      env_var(env, 'PYTHONPATH').append(substituted.data.pythonpath)

  def cleanup_python_compiled_files(self):
    root_dirs = [ config.root_dir for config in self._env_dependencies_configs ]
    pyc_files = file_finder.find_python_compiled_files(root_dirs)
    file_util.remove(pyc_files)

  def _file_is_managed(self, filename):
    'Return True if filename is managed by the environment.'
    for config in self._env_dependencies_configs:
      if filename.startswith(config.root_dir):
        return True
    return False

  def print_configs(self):
    data = sorted([ ( c.data.name, c.nice_filename ) for c in self.config_env.config_map.values() ])
    from bes.text import text_table, text_cell_renderer
    max_width = max([ len(row[0]) for row in data ])
    tt = text_table(data = data, column_delimiter = ' ')
    tt.set_col_renderer(0, text_cell_renderer(just = text_cell_renderer.JUST_LEFT, width = max_width))
    print(tt)
