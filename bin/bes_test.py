#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

# A script to run python unit tests.  Does not use any bes code to avoid
# chicken-and-egg issues.
import argparse, ast, fnmatch, math, os, os.path as path, platform, random, re, subprocess, sys
from collections import namedtuple

# TODO:
#  - figure out how to stop on first failure within one module
#  - https://stackoverflow.com/questions/6813837/stop-testsuite-if-a-testcase-find-an-error

#class bes_test_command_line(object):
#
#  def __init__(self):
#    pass

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('files', action = 'store', nargs = '*', help = 'Files or directories to rename')
  parser.add_argument('--unit',
                      '-u',
                      action = 'store_true',
                      default = False,
                      help = 'Just run unit tests [ False ]')
  parser.add_argument('--dry-run',
                      '-n',
                      action = 'store_true',
                      default = False,
                      help = 'Only print what files will get tests [ False ]')
  parser.add_argument('--verbose',
                      '-v',
                      action = 'store_true',
                      default = False,
                      help = 'Verbose debug spew [ False ]')
  parser.add_argument('--stop',
                      '-s',
                      action = 'store_true',
                      default = False,
                      help = 'Stop right after the first failure. [ False ]')
  parser.add_argument('--randomize',
                      '-r',
                      action = 'store_true',
                      default = False,
                      help = 'Randomize the order in which unit tests run. [ False ]')
  parser.add_argument('--python',
                      '-p',
                      action = 'store',
                      default = 'python',
                      help = 'Python executable to use [ python ]')
  parser.add_argument('--git',
                      '-g',
                      action = 'store_true',
                      default = False,
                      help = 'Use git status to figure out what has changed to test [ False ]')
  parser.add_argument('--dump',
                      '-d',
                      action = 'store_true',
                      default = False,
                      help = 'Dump the list of unit tests [ False ]')
  args = parser.parse_args()

  files, filters = _separate_files_and_filters(args.files)
  if not files:
    files = []
    
  if args.git:
    items = _git_status()
    modified_files = [ item.filename for item in items if 'M' in item.modifier ]
    modified_py_files = [ f for f in modified_files if f.endswith('.py') ]
    files.extend(modified_py_files)
    
  files = _resolve_files(_unique_list(files))
  files = sorted(_unique_list(files))

  if args.randomize:
    random.shuffle(files)

  available_unit_tests = _available_unit_tests(files)

  if args.dump:
    _dump_available_unit_tests(available_unit_tests)
    return 0
  
  patterns = _make_filters_patterns(filters)

  filename_patterns = [ p.filename for p in patterns if p.filename ]
  if filename_patterns:
    files = _match_filenames(files, filename_patterns)

  filtered_files = _filter_files(files, available_unit_tests, patterns)
  
  num_passed = 0
  num_failed = 0
  num_executed = 0
  num_tests = len(filtered_files)
  failed_tests = []
  for i, f in enumerate(filtered_files):
    success = _python_call(args.python, f.filename, f.tests, args.dry_run, args.verbose,
                           args.stop, i + 1, len(filtered_files))
    num_executed += 1
    if success:
      num_passed += 1
    else:
      num_failed += 1
      failed_tests.append(f)

    if args.stop and not success:
      break
  num_skipped = num_tests - num_executed
  summary_parts = []
  if num_failed > 0:
    summary_parts.append('%d of %d FAILED' % (num_failed, num_tests))
  summary_parts.append('%d of %d passed' % (num_passed, num_tests))
  if num_skipped > 0:
    summary_parts.append('%d of %d skipped' % (num_skipped, num_tests))

  summary = '; '.join(summary_parts)
  print 'bes_test.py: %s' % (summary)
  if failed_tests:
    for f in failed_tests:
      print 'bes_test.py: FAILED: %s' % (path.relpath(f.filename))
  
  if num_failed > 0:
    return 1
  return 0

def _resolve_files(files):
  result = []
  for f in files:
    if path.isfile(f):
      result.append(path.abspath(path.normpath(f)))
    elif path.isdir(f):
      result += _find_tests(f)
  result = _unique_list(result)
  more_tests = []
  for r in result:
    more_tests.extend(_tests_for_file(r))
  result.extend(more_tests)
  result = [ r for r in result if _file_has_tests(r) ]
  result = [ path.normpath(r) for r in result ]
  return sorted(result)
  
file_and_tests = namedtuple('file_and_tests', 'filename,tests')
def _filter_files(files, available, patterns):
  if not patterns:
    return [ file_and_tests(filename, None) for filename in files ]
  result = []
  for filename in files:
#    print "filename: ", filename
#    print "available: "
#    for k in sorted(available.keys()):
#      print "  next: ", k
#      for x in available[k]:
#        print "    ", x
    assert filename in available
    available_for_filename = available[filename]
    matching_tests = _matching_tests(available_for_filename, patterns)
    if matching_tests:
      result.append(file_and_tests(filename, matching_tests))
  return result
    
def _tests_for_file(filename):
  basename = path.basename(filename)
  dirname = path.dirname(filename)
  name = path.splitext(basename)[0]
  test_filename = 'test_%s.py' % (name)
  tests_dir = path.join(dirname, 'tests', test_filename)
  if path.exists(tests_dir):
    return [ tests_dir ]
  return []

def _file_read(filename):
  with open(filename, 'r') as fin:
    return fin.read()

def _file_has_tests(filename):
  content = _file_read(filename)
  if content.find('unittest.TestCase') >= 0:
    return True
  if content.find('unit_test_helper') >= 0:
    return True
  return False

unit_test_desc = namedtuple('unit_test_desc', 'filename,fixture,function')
def _available_unit_tests(filenames):
  available = {}
  for filename in filenames:
    available[filename] = []
              
  for filename in filenames:
    code = _file_read(filename)
    tree = ast.parse(code)
    for node in tree.body:
      if isinstance(node, ast.ClassDef):
        for statement in node.body:
          if isinstance(statement, ast.FunctionDef):
            available[filename].append(unit_test_desc(filename, node.name, statement.name))
  return available

def _dump_available_unit_tests(available):
  for filename in sorted(available.keys()):
    for _, fixture, function in available[filename]:
      print '%s:%s.%s' % (filename, fixture, function)

def _find_tests(d):
  cmd = [ 'find', d, '-name', 'test_*.py' ]
  result = subprocess.check_output(cmd, shell = False)
  return [ f for f in result.strip().split('\n') if f ]

def _filepath_normalize(filepath):
  f = path.abspath(path.normpath(filepath))
  if path.exists(f):
    return f
  return None

def _filepaths_normalize(files):
  return [ _filepath_normalize(f) for f in files ]

def _which(exe):
  cmd = [ 'which', exe ]
  try:
    return subprocess.check_output(cmd, shell = False).strip()
  except:
    return None

def _short_filename(filename):
  head = os.getcwd() + os.sep
  if filename.startswith(head):
    return filename[len(head):]
  return filename

def __system():
  return platform.system().lower()

def __conditional_resolve(conditional):
  s = __system()
  replacements = {
    '${system}': __system(),
  }
  cond_key = conditional.key
  for replacement_key, replacement_value in replacements.items():
    cond_key = cond_key.replace(replacement_key, replacement_value)
  return Conditional(cond_key, conditional.operator, conditional.value)

def __conditional_evaluate(conditional):
  assert conditional.operator in [ '==', '!=' ]
  if conditional.operator == '==':
    return conditional.key == conditional.value
  elif conditional.operator == '!=':
    return conditional.key != conditional.value
  assert False

def __conditionals_evaluate(conditionals):
  return not False in [ __conditional_evaluate(c) for c in conditionals ]

def _matching_tests(available, patterns):
  result = []
  for test in available:
    for pattern in patterns:
      fixture_matches = True
      if pattern.fixture:
        fixture_matches = fnmatch.fnmatch(test.fixture.lower(), pattern.fixture.lower())
      function_matches = True
      if pattern.function:
        function_matches = fnmatch.fnmatch(test.function.lower(), pattern.function.lower())
      if fixture_matches and function_matches:
        result.append(test)
  return result

def _python_call(python, filename, tests, dry_run, verbose,
                 stop_on_failure, index, total):
  short_filename = _short_filename(filename)
  cmd = [ python, '-B', filename ]

  if tests:
    cmd.extend([ '%s.%s' % (test.fixture, test.function) for test in tests ])
  
  try:
#    if stop:
#      cmd.append('--stop')
    if dry_run:
      print short_filename
      return True

    if total > 1:
      count_blurb = ' ' + _make_count_blurb(index, total)
    else:
      count_blurb = ''
    print('bes_test.py:%7s:%s %s' % ('testing', count_blurb, short_filename))

    stdout_pipe = subprocess.PIPE
    if not verbose:
      stderr_pipe = subprocess.PIPE
    else:
      stderr_pipe = subprocess.STDOUT

    process = subprocess.Popen(' '.join(cmd),
                               stdout = stdout_pipe,
                               stderr = stderr_pipe,
                               shell = True,
                               env = _make_clean_env())
    output = process.communicate()
    exit_code = process.wait()

    stdout_output = output[0]
    stderr_output = output[1]
    success = exit_code == 0
    spew_output = not success or verbose
    if success:
      label = 'passed'
    else:
      label = 'FAILED'
    if spew_output:
      print 'bes_test.py: %7s: %s' % (label, short_filename)
      sys.stdout.write(stdout_output)
      if not success:
        sys.stdout.write(stderr_output)
      sys.stdout.flush()
    return success
  except Exception, ex:
    print 'bes_test.py: Caught exception on %s: %s' % (filename, str(ex))
    return False

def _match_test(patterns, filename):
  filename = filename.lower()
  for pattern in patterns:
    if fnmatch.fnmatch(s, pattern.lower()):
      return True
  return False

def _search_for_tests(search_patterns, where):
  result = []
  possible_tests = _find_tests(where)
  for filename in possible_tests:
    if _match_test(search_patterns, filename):
      result.append(filename)
  return sorted(_unique_list(result))

def _is_fnmatch_pattern(pattern):
  for c in [ '*', '?', '[', ']', '!' ]:
    if pattern.count(c) > 0:
      return True
  return False

def _make_fnmatch_pattern(pattern):
  pattern = pattern.lower()
  if _is_fnmatch_pattern(pattern):
    return pattern
  return '*%s*' % (pattern)

def _unique_list(l):
  return list(set(l))

def _make_clean_env():
  'Return a clean environment suitable for deterministic build related tasks.'
  clean_path = '/bin:/usr/bin:/usr/sbin:/sbin'
  clean_vars = [ 'BES_LOG', 'PYTHONPATH', 'DISPLAY', 'HOME', 'LANG', 'SHELL', 'TERM', 'TERM_PROGRAM', 'TMOUT', 'TMPDIR', 'USER', 'XAUTHORITY', '__CF_USER_TEXT_ENCODING' ]
  clean_env = {}
  for k, v in os.environ.items():
    if k in clean_vars:
      clean_env[k] = v
  clean_env['PATH'] = clean_path
  return clean_env

def _make_count_blurb(index, total):
  length = int(math.log10(total)) + 1
  index = str(index)
  count = str(total)
  index_blurb = (' ' * (length - len(index))) + index
  count_blurb = (' ' * (length - len(count))) + count
  return '[%s of %s]' % (index_blurb, count_blurb)

git_status_item = namedtuple('git_status_item', 'modifier,filename')
def _git_parse_status_line(line):
  line = line.strip()
  v = re.findall('\s*(\w+)\s+(.*)', line)
  if len(v) != 1:
    return None
  assert len(v[0]) == 2
  modifier = v[0][0]
  filename = v[0][1]
  return git_status_item(modifier, filename)

def _git_status():
  cmd = [ 'git', 'st', '--porcelain', '.' ]
  result = subprocess.check_output(cmd, shell = False)
  items = [ _git_parse_status_line(line) for line in result.split('\n') if line.strip() ]
  return [ item for item in items if item ]

def _parse_unit_test_desc(s):
  'Parse a unit test description in the form filename:fixutre.function'
  filename, _, right = s.partition(':')
  if '.' in right:
    fixture, _, function = right.partition('.')
  else:
    fixture, function = ( None, right )
  return unit_test_desc(filename, fixture or None, function or None)

files_and_filters = namedtuple('files_and_filters', 'files,filters')
def _separate_files_and_filters(args):
  files = []
  filter_descriptions = []
  for f in args:
    normalized_path = _filepath_normalize(f)
    if not normalized_path:
      filter_descriptions.append(f)
    else:
      files.append(f)
  filters = [ _parse_unit_test_desc(f) for f in (filter_descriptions or []) ]
  return files_and_filters(files, filters)

  files, filters = _separate_files_and_filters(args.files)
  if not files:
    files = []

def _make_filters_patterns(filters):
  patterns = []
  for f in filters:
    filename_pattern = None
    fixture_pattern = None
    function_pattern = None
    if f.filename:
      filename_pattern = _make_fnmatch_pattern(f.filename)
    if f.fixture:
      fixture_pattern = _make_fnmatch_pattern(f.fixture)
    if f.function:
      function_pattern = _make_fnmatch_pattern(f.function)
    patterns.append(unit_test_desc(filename_pattern, fixture_pattern, function_pattern))
  return patterns

def _match_filenames(files, patterns):
  result = []
  for filename in files:
    if _match_test(patterns, filename):
      result.append(filename)
  return sorted(_unique_list(result))

import unittest

class test_bes_test(unittest.TestCase):

  def test_parse_unit_test_desc(self):
    
    self.assertEqual( ( 'foo.py', 'fix', 'func' ), _parse_unit_test_desc('foo.py:fix.func') )
    self.assertEqual( ( 'foo.py', None, None ), _parse_unit_test_desc('foo.py') )
    self.assertEqual( ( 'foo.py', None, None ), _parse_unit_test_desc('foo.py:') )
    self.assertEqual( ( 'foo.py', None, 'fix' ), _parse_unit_test_desc('foo.py:fix') )

if len(sys.argv) == 2 and sys.argv[1] in [ '--unit', '-u' ]:
  sys.argv = sys.argv[0:1]
  unittest.main()
  
if __name__ == '__main__':
  raise SystemExit(main())

    
