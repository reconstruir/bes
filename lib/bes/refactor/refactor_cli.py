#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path

from bes.fs.file_resolve import file_resolve

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

  def _command_rename(self, src, dst, dirs, dry_run, word_boundary):
    refactor_files.refactor(src, dst, dirs, word_boundary = word_boundary)
    
  def _command_list(self, files):
    files = file_resolve.resolve_files(files, patterns = '*.py')
    for f in files:
      print(f)
    return 0
  
  def _command_rename_dirs(self, src, dst, d, dry_run, word_boundary):
    print('_command_rename_dirs(%s, %s, %s, %s, %s)' % (src, dst, d, dry_run, word_boundary))
    refactor_files.rename_dirs(src, dst, d, word_boundary = word_boundary)
    #refactor_files.refactor(src, dst, dirs, word_boundary = word_boundary)
    
