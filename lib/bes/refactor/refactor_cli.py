#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path

from bes.fs.file_resolve import file_resolve

from .import_expand import import_expand

from .files import files as refactor_files

class refactor_cli(object):

  def __init__(self):

    self._parser = argparse.ArgumentParser()

    subparsers = self._parser.add_subparsers(help = 'commands', dest = 'command')

    # Rename
    rename_parser = subparsers.add_parser('rename', help = 'Rename a module')
    rename_parser.add_argument('src', action = 'store', type = str, help = 'Source string.')
    rename_parser.add_argument('dst', action = 'store', type = str, help = 'Destination string.')
    rename_parser.add_argument('dirs', action = 'store', nargs = '+', help = 'Directories to refactor')
    rename_parser.add_argument('--dry-run', '-n', action = 'store_true', default = False,
                               help = 'Only print what would happen without doing it [ False ]')
    rename_parser.add_argument('--word-boundary', '-w', action = 'store_true', default = False,
                               help = 'Respect word boundaries [ False ]')

    # expand imports
    p = subparsers.add_parser('expand_imports', help = 'Example imports')
    p.add_argument('namespace', action = 'store', help = 'Namespace to expand')
    p.add_argument('files', action = 'store', nargs = '+', help = 'Files or directories to refactor')
    p.add_argument('--dry-run', '-n', action = 'store_true', default = False,
                   help = 'Only print what would happen without doing it [ False ]')
    p.add_argument('--sort', action = 'store_true', default = False,
                   help = 'Sort the new list if imports [ False ]')
    p.add_argument('--include-module', '-i', action = 'store_true', default = False,
                   help = 'Include the module in the new import line. [ False ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose spew about what the tool is doing. [ False ]')
    
    # Rename dirs
    rename_dirs_parser = subparsers.add_parser('rename_dirs', help = 'Rename_Dirs a module')
    rename_dirs_parser.add_argument('src', action = 'store', type = str, help = 'Source string.')
    rename_dirs_parser.add_argument('dst', action = 'store', type = str, help = 'Destination string.')
    rename_dirs_parser.add_argument('dir', action = 'store', help = 'Directory tree to rename.')
    rename_dirs_parser.add_argument('--dry-run', '-n', action = 'store_true', default = False,
                                    help = 'Only print what would happen without doing it [ False ]')
    rename_dirs_parser.add_argument('--word-boundary', '-w', action = 'store_true', default = False,
                                    help = 'Respect word boundaries [ False ]')
    rename_dirs_parser.add_argument('--content-only', action = 'store_true', default = False,
                                    help = 'Rename content of files only [ False ]')

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

    # list
    list_parser = subparsers.add_parser('list', help = 'Resolve and list what files would be part of a refactor.')
    list_parser.add_argument('files', action = 'store', nargs = '*', help = 'Files or directories to resolve and list')
    
  @classmethod
  def run(clazz):
    raise SystemExit(refactor_cli().main())

  def main(self):
    args = self._parser.parse_args()
    if args.command == 'rename':
      return self._command_rename(args.src, args.dst, args.dirs, args.dry_run, args.word_boundary)
    if args.command == 'rename_dirs':
      return self._command_rename_dirs(args.src, args.dst, args.dir, args.dry_run, args.word_boundary)
    elif args.command == 'unit':
      return self._command_unit(self.filepaths_normalize(args.files), args.dry_run, args.limit, args.backup)
    elif args.command == 'unit_cleanup':
      return self._command_unit_cleanup(self.filepaths_normalize(args.files), args.dry_run)
    elif args.command == 'list':
      return self._command_list(self.filepaths_normalize(args.files))
    elif args.command == 'expand_imports':
      return self._command_expand_imports(args.namespace, args.files, args.include_module, args.sort, args.dry_run, args.verbose)

  def _command_rename(self, src, dst, dirs, dry_run, word_boundary):
    refactor_files.refactor(src, dst, dirs, word_boundary = word_boundary)
    
  NEW_CONTENT_HEADER = '''\
  #!/usr/bin/env python
  #-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
  #
  '''
  
  def _command_unit_process_one_file(self, filename, dry_run, make_backup):
    content = file_util.read(filename)
    if not self._file_has_unit_tests(content):
      #print 'bes_refactor.py: No unit tests found: %s' % (filename)
      return False
    test_module_path = _test_module_path(filename)
    if path.exists(test_module_path):
      print('bes_refactor.py: test module already exists for %s: %s' % (filename, test_module_path))
      return False
    lines = content.split('\n')
    span = self._file_find_unit_tests_span(filename, lines)
    if span:
      commented_lines = _comment_span(lines, span)
      commented_content = '\n'.join(commented_lines)
      new_content_lines = lines[span[0]:span[1]]
      new_content = clazz.NEW_CONTENT_HEADER + '\n'.join(new_content_lines)
      if make_backup:
        file_util.backup(filename)
      file_util.save(filename, content = commented_content, mode = 0o755)
      _span_save(span, filename + '.span')
      file_util.save(test_module_path, content = new_content, mode = 0o755)
      git.add(os.getcwd(), test_module_path)
      return True
    return False
  
  def _command_unit(self, files, dry_run, limit, make_backup):
    files = file_resolve.resolve_files(files, patterns = '*.py')
    success_count = 0
    for f in files:
      if _command_unit_process_one_file(f, dry_run, make_backup):
        success_count += 1
        print('bes_refactor.py: Successfully processed: %s' % (f))
      if success_count == limit:
        print('bes_refactor.py: reached limit of %d' % (limit))
        break
    return 0
  
  def _command_unit_cleanup_one_file(self, span_filename, dry_run):
    filename = file_util.remove_extension(span_filename)
    assert path.exists(filename)
    span = self._span_read(span_filename)
    assert span
    lines = file_util.read(filename).split('\n')
    for i in range(span[0], span[1]):
      line = lines[i]
      assert lines[i].startswith(COMMENTED_OUT_HEAD)
    new_content_lines = lines[:]
    new_content_lines[span[0]:span[1]] = []
    new_content = '\n'.join(new_content_lines)
    file_util.save(filename, content = new_content, mode = 0o755)
    file_util.remove(span_filename)
    return True
    
  def _command_unit_cleanup(self, files, dry_run):
    files = file_resolve.resolve_files(files, patterns = '*.span')
    for f in files:
      self._command_unit_cleanup_one_file(f, dry_run)
    return 0

  def _command_list(self, files):
    files = file_resolve.resolve_files(files, patterns = '*.py')
    for f in files:
      print(f)
    return 0
  
  UNIT_TESTS_MARKER = 'unittest.TestCase'
      
  @classmethod
  def _file_has_unit_tests(clazz, content):
    return content.find(clazz.UNIT_TESTS_MARKER) >= 0
  
  @classmethod
  def _file_find_unit_tests_span(clazz, filename, lines):
    unit_test_lines = _file_lines_find_unit_tests_instances(lines)
    if len(unit_test_lines) != 1:
      print('bes_refactor.py: %s: too many tests.  fix it by hand.' % (filename))
      
  
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
  
  @classmethod
  def _find_def_backwards(clazz, alines, start_line):
    for line_number in reversed(range(0, start_line)):
      line = lines[line_number]
      def_indent = _parse_def_indent(line)
      if def_indent is not None:
        return ( def_indent, line_number )
    return None
  
  @classmethod
  def _find_indent_less_than(clazz, lines, start_line, greater_indent):
    for line_number in range(start_line, len(lines)):
      line = lines[line_number]
      indent = _count_indent(line)
      if indent is not None:
        if indent < greater_indent:
          return line_number
    return None
  
  @classmethod
  def _count_indent(clazz, line):
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
    
  @classmethod
  def _file_lines_find_unit_tests_instances(clazz, lines):
    result = []
    for line_number, line in enumerate(lines):
      if line.find(clazz.UNIT_TESTS_MARKER) >= 0:
        result.append(line_number)
    return result
    
  @classmethod
  def _test_module_path(clazz, filepath):
    assert path.isabs(filepath)
    dirname = path.dirname(filepath)
    basename = path.basename(filepath)
    name = path.splitext(basename)[0]
    test_module_filename = 'test_%s.py' % (name)
    return path.join(dirname, 'tests', test_module_filename)
  
  @classmethod
  def _parse_def_indent(clazz, line):
    assert not '\t' in line
    s = re.search(r'\bdef\b', line)
    if not s:
      return None
    return s.span()[0]

  @classmethod
  def _comment_span(clazz, lines, span):
    lines = lines[:]
    for line_number in range(span[0], span[1]):
      lines[line_number] = '%s%s' % (COMMENTED_OUT_HEAD, lines[line_number])
    return lines
  
  @classmethod
  def _span_save(clazz, span, filename):
    json_util.save_file(filename, span, indent = 2)
  
  @classmethod
  def _span_read(clazz, filename):
    o = json_util.read_file(filename)
    assert isinstance(o, ( tuple, list ))
    assert len(o) == 2
    return tuple(o)

  def _command_rename_dirs(self, src, dst, d, dry_run, word_boundary):
    print('_command_rename_dirs(%s, %s, %s, %s, %s)' % (src, dst, d, dry_run, word_boundary))
    refactor_files.rename_dirs(src, dst, d, word_boundary = word_boundary)
    #refactor_files.refactor(src, dst, dirs, word_boundary = word_boundary)
    
  def _command_expand_imports(self, namespace, files, include_module, sort, dry_run, verbose):
    files = file_resolve.resolve_files(files, patterns = '*.py')
    import_expand.expand(namespace, files, include_module, sort, dry_run, verbose)
    
