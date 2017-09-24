#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# bes:skip_unit_test=1

import argparse, os, os.path as path, re, sys

from bes.common import algorithm, json_util
from bes.fs import file_find, file_match, file_replace, file_util, file_path
from bes.archive import archiver
from bes.git import git
from bes.refactor import files as refactor_files

#log.configure('file_find=debug')

COMMENTED_OUT_HEAD = '#####'

def main():
  
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(help = 'commands', dest = 'command')

  # Rename
  rename_parser = subparsers.add_parser('rename', help = 'Rename a module')
  rename_parser.add_argument('src', action = 'store', type = str, help = 'Source string.')
  rename_parser.add_argument('dst', action = 'store', type = str, help = 'Destination string.')
  rename_parser.add_argument('dirs', action = 'store', nargs = '+', help = 'Directories to refactor')
  rename_parser.add_argument('--dry-run', '-n', action = 'store_true', default = False,
                             help = 'Only print what would happen without doing it [ False ]')
  rename_parser.add_argument('--word-boundary', '-w', action = 'store_true', default = False,
                             help = 'Respect word boundaries [ False ]')

  # Unit
  unit_parser = subparsers.add_parser('unit', help = 'Ensure unit tests are in their own modules.')
  unit_parser.add_argument('files', action = 'store', nargs = '*', help = 'Files or directories to unit')
  unit_parser.add_argument('--dry-run',
                           '-n',
                           action = 'store_true',
                           default = False,
                           help = 'Only print what would happen without doing it [ False ]')
  unit_parser.add_argument('--limit',
                           '-l',
                           action = 'store',
                           default = None,
                           type = int,
                           help = 'Limit processing to given number of files [ None ]')
  unit_parser.add_argument('--backup',
                           action = 'store_true',
                           default = False,
                           help = 'Whether to make backups of refatored files [ False ]')

  # Unit cleanup
  unit_cleanup_parser = subparsers.add_parser('unit_cleanup', help = 'Ensure unit tests are in their own modules.')
  unit_cleanup_parser.add_argument('files', action = 'store', nargs = '*', help = 'Files or directories to unit')
  unit_cleanup_parser.add_argument('--dry-run',
                                   '-n',
                                   action = 'store_true',
                                   default = False,
                                   help = 'Only print what would happen without doing it [ False ]')

  args = parser.parse_args()

  if args.command == 'rename':
    return _command_rename(args.src, args.dst, args.dirs, args.dry_run, args.word_boundary)
  elif args.command == 'unit':
    return _command_unit(_filepaths_normalize(args.files), args.dry_run, args.limit, args.backup)
  elif args.command == 'unit_cleanup':
    return _command_unit_cleanup(_filepaths_normalize(args.files), args.dry_run)
  assert False, 'Not reached'
  return 0

EXCLUDED_FILES = [
  '*/site/Linux/*',
  '*/site/Darwin/*',
  '*/site/Common/*',
  '*/__init__.py',
  '*/projects/scripts/*',
  '*/tests/test_*.py',
]

def _filepath_normalize(filepath):
  return path.abspath(path.normpath(filepath))

def _filepaths_normalize(files):
  return [ _filepath_normalize(f) for f in files ]

def _resolve_files(files, patterns = None):
  'Resolve a mixed list of files and directories into a sorted list of files.'
  result = []
  for f in files:
    if not path.exists(f):
      raise RuntimeError('Not found: %s' % (f))
    if path.isfile(f):
      result.append(path.abspath(path.normpath(f)))
    elif path.isdir(f):
      result += file_find.find_fnmatch(f, patterns, relative = False)
    result = sorted(algorithm.unique(result))
    return file_match.match_fnmatch(result, EXCLUDED_FILES, file_match.NONE)
  
def _command_rename(src, dst, dirs, dry_run, word_boundary):
  refactor_files.refactor(src, dst, dirs, word_boundary = word_boundary)
  
NEW_CONTENT_HEADER = '''\
#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
'''

def _command_unit_process_one_file(filename, dry_run, make_backup):
  content = file_util.read(filename)
  if not _file_has_unit_tests(content):
    #print 'bes_refactor.py: No unit tests found: %s' % (filename)
    return False
  test_module_path = _test_module_path(filename)
  if path.exists(test_module_path):
    print('bes_refactor.py: test module already exists for %s: %s' % (filename, test_module_path))
    return False
  lines = content.split('\n')
  span = _file_find_unit_tests_span(lines)
  if span:
    commented_lines = _comment_span(lines, span)
    commented_content = '\n'.join(commented_lines)
    new_content_lines = lines[span[0]:span[1]]
    new_content = NEW_CONTENT_HEADER + '\n'.join(new_content_lines)
    if make_backup:
      file_util.backup(filename)
    file_util.save(filename, content = commented_content, mode = 0755)
    _span_save(span, filename + '.span')
    file_util.save(test_module_path, content = new_content, mode = 0755)
    git.add(os.getcwd(), test_module_path)
    return True
  return False

def _command_unit(files, dry_run, limit, make_backup):
  files = _resolve_files(files, patterns = '*.py')
  success_count = 0
  for f in files:
    if _command_unit_process_one_file(f, dry_run, make_backup):
      success_count += 1
      print('bes_refactor.py: Successfully processed: %s' % (f))
    if success_count == limit:
      print('bes_refactor.py: reached limit of %d' % (limit))
      break
  return 0

def _command_unit_cleanup_one_file(span_filename, dry_run):
  filename = file_util.remove_extension(span_filename)
  assert path.exists(filename)
  span = _span_read(span_filename)
  assert span
  lines = file_util.read(filename).split('\n')
  for i in range(span[0], span[1]):
    line = lines[i]
    assert lines[i].startswith(COMMENTED_OUT_HEAD)
  new_content_lines = lines[:]
  new_content_lines[span[0]:span[1]] = []
  new_content = '\n'.join(new_content_lines)
  file_util.save(filename, content = new_content, mode = 0755)
  file_util.remove(span_filename)
  return True
  
def _command_unit_cleanup(files, dry_run):
  files = _resolve_files(files, patterns = '*.span')
  for f in files:
    _command_unit_cleanup_one_file(f, dry_run)
  return 0

UNIT_TESTS_MARKER = 'unittest.TestCase'
    
def _file_has_unit_tests(content):
  return content.find(UNIT_TESTS_MARKER) >= 0

def _file_find_unit_tests_span(lines):
  unit_test_lines = _file_lines_find_unit_tests_instances(lines)
  assert len(unit_test_lines) == 1

  unit_test_line_number = unit_test_lines[0]
  assert unit_test_line_number >= 0
  assert unit_test_line_number < len(lines)

  try: 
    def_indent, def_line_number = _find_def_backwards(lines, unit_test_line_number)
  except:
    return None

  less_than_line_number = _find_indent_less_than(lines, def_line_number, def_indent)
  if less_than_line_number is None:
    return None

  return ( less_than_line_number, len(lines) )

def _find_def_backwards(lines, start_line):
  for line_number in reversed(range(0, start_line)):
    line = lines[line_number]
    def_indent = _parse_def_indent(line)
    if def_indent is not None:
      return ( def_indent, line_number )
  return None

def _find_indent_less_than(lines, start_line, greater_indent):
  for line_number in range(start_line, len(lines)):
    line = lines[line_number]
    indent = _count_indent(line)
    if indent is not None:
      if indent < greater_indent:
        return line_number
  return None

def _count_indent(line):
  assert not line is None
  if len(line) == 0:
    return None
  if line.isspace():
    return None
  count = 0
  for c in line:
    if c == ' ':
      count += 1
    else:
      break
  return count
  
def _file_lines_find_unit_tests_instances(lines):
  result = []
  for line_number, line in enumerate(lines):
    if line.find(UNIT_TESTS_MARKER) >= 0:
      result.append(line_number)
  return result
  
def _test_module_path(filepath):
  assert path.isabs(filepath)
  dirname = path.dirname(filepath)
  basename = path.basename(filepath)
  name = path.splitext(basename)[0]
  test_module_filename = 'test_%s.py' % (name)
  return path.join(dirname, 'tests', test_module_filename)

def _parse_def_indent(line):
  assert not '\t' in line
  s = re.search(r'\bdef\b', line)
  if not s:
    return None
  return s.span()[0]

def _comment_span(lines, span):
  lines = lines[:]
  for line_number in range(span[0], span[1]):
    lines[line_number] = '%s%s' % (COMMENTED_OUT_HEAD, lines[line_number])
  return lines

def _span_save(span, filename):
  json_util.save_file(filename, span, indent = 2)

def _span_read(filename):
  o = json_util.read_file(filename)
  assert isinstance(o, ( tuple, list ))
  assert len(o) == 2
  return tuple(o)

import unittest
from bes.fs import temp_file
class TestRefactorScript(unittest.TestCase):

  def test_find_unit_tests_span(self):
    content = '''
import re,sys

class Foo(object):
  def myfunc(self):
    pass

import unittest

import re

class TestFoo(unittest.TestCase):
  def test_foo1(self):
    pass

  def test_foo2(self):
    pass

if __name__ == "__main__":
  unittest.main()
'''
    expected_span = ( 7, 21 )
    lines = content.split('\n')
    actual_span = _file_find_unit_tests_span(lines)
    self.assertEqual( expected_span, actual_span )

  def test_parse_def_indent(self):
    self.assertEqual( 0, _parse_def_indent('def foo():') )
    self.assertEqual( 2, _parse_def_indent('  def foo():') )
    self.assertEqual( 4, _parse_def_indent('    def foo():') )
    self.assertEqual( None, _parse_def_indent('adef = 5') )

  def test_span_save_read(self):
    expected_span = ( 6, 7 )
    tmp = temp_file.make_temp_file()
    _span_save(expected_span, tmp)
    actual_span = _span_read(tmp)
    self.assertEqual( expected_span, actual_span )

if __name__ == '__main__':
  sys.exit(main())
