#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from os import path

from bes.common.algorithm import algorithm
from bes.fs.dir_util import dir_util
from bes.fs.file_mime import file_mime
from bes.files.bf_path import bf_path
from bes.fs.file_replace import file_replace
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options
from bes.fs.file_search import file_search
from bes.fs.file_util import file_util
from bes.fs.filename_util import filename_util
from bes.system.check import check
from bes.system.log import logger
from bes.system.python import python
from bes.text.text_detect import text_detect

from .refactor_error import refactor_error
from .refactor_item import refactor_item
from .refactor_operation_type import refactor_operation_type
from .refactor_options import refactor_options
from .refactor_reindent import refactor_reindent

class refactor_files(object):

  @classmethod
  def resolve_python_files(clazz, files):
    'Resolve python files.'
    check.check_string_seq(files)

    def _match_python_files(filename):
      if not text_detect.file_is_text(filename):
        return False
      if python.is_python_script(filename):
        return True
      return filename_util.has_extension(filename.lower(), 'py')
    resolver_options = file_resolver_options(recursive = True,
                                             match_function = _match_python_files,
                                             match_basename = False)
    resolved = file_resolver.resolve_files(files, options = resolver_options)
    return resolved.absolute_files(sort = True)

  @classmethod
  def resolve_text_files(clazz, files):
    'Resolve text files.'
    check.check_string_seq(files)
    
    def _match_text_files(filename):
      if path.islink(filename):
        return False
      if file_util.is_empty(filename):
        return False
      return text_detect.file_is_text(filename)
    resolver_options = file_resolver_options(recursive = True,
                                             match_function = _match_text_files,
                                             match_basename = False)
    resolved = file_resolver.resolve_files(files, options = resolver_options)
    return resolved.absolute_files(sort = True)

  _affected_dir = namedtuple('_affected_dir', 'root_dir, dirname')
  _log = logger('refactor')
  @classmethod
  def rename_files(clazz, files, src_pattern, dst_pattern, options = None):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_refactor_options(options, allow_none = True)

    clazz._log.log_method_d()
    options = options or refactor_options()
    return clazz._do_operation(refactor_operation_type.RENAME_FILES,
                               files,
                               src_pattern,
                               dst_pattern,
                               False,
                               options)

  @classmethod
  def copy_files(clazz, files, src_pattern, dst_pattern, copy_dirs, options = None):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_refactor_options(options, allow_none = True)
    check.check_bool(copy_dirs)

    clazz._log.log_method_d()
    options = options or refactor_options()
    return clazz._do_operation(refactor_operation_type.COPY_FILES,
                               files,
                               src_pattern,
                               dst_pattern,
                               copy_dirs,
                               options)
    
  @classmethod
  def rename_dirs(clazz, dirs, src_pattern, dst_pattern, options = None):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_refactor_options(options, allow_none = True)
    
    options = options or refactor_options()
    clazz._log.log_method_d()

    resolved_empty_dirs = file_resolver.resolve_empty_dirs(dirs, recursive = True)
    # we need to figure out if there any empty directories that match the pattern
    # so we can manually rename them, since the _do_operation function only deal
    # with files.
    empty_dirs_operation_items, empty_dirs_affected_dirs = \
      clazz._make_operation_items(refactor_operation_type.RENAME_DIRS,
                                  resolved_empty_dirs,
                                  src_pattern,
                                  dst_pattern,
                                  False,
                                  options.word_boundary,
                                  options.word_boundary_chars)
    result = clazz._do_operation(refactor_operation_type.RENAME_DIRS,
                                 dirs,
                                 src_pattern,
                                 dst_pattern,
                                 False,
                                 options)
    for item in empty_dirs_operation_items:
      file_util.mkdir(item.dst)
      assert dir_util.is_empty(item.src)
      dir_util.remove(item.src)
    
    for d in empty_dirs_affected_dirs:
      if path.exists(d) and dir_util.is_empty(d):
        dir_util.remove(d)
        
    return result

  @classmethod
  def _do_operation(clazz, operation, dirs, src_pattern, dst_pattern, copy_dirs, options):
    assert options
    resolver_options = file_resolver_options(recursive = True,
                                             sort_order = 'depth',
                                             sort_reverse = True)
    resolved_files = file_resolver.resolve_files(dirs, options = resolver_options)
    operation_items, affected_dirs = \
      clazz._make_operation_items(operation,
                                  resolved_files,
                                  src_pattern,
                                  dst_pattern,
                                  copy_dirs,
                                  options.word_boundary,
                                  options.word_boundary_chars)

    for next_operation_item in operation_items:
      is_safe = next_operation_item.is_safe(operation)
      if not is_safe.safe:
        if options.unsafe:
          options.blurber.blurb(f'UNSAFE: {is_safe.reason}')
        else:
          raise RuntimeError(is_safe.reason)
      
    new_dirs = algorithm.unique([ path.dirname(item.dst) for item in operation_items ])
    new_dirs = [ d for d in new_dirs if d and not path.exists(d) ]
    for next_new_dir in new_dirs:
      file_util.mkdir(next_new_dir)
    for next_operation_item in operation_items:
      next_operation_item.apply_operation(operation, options.try_git)
    if operation != refactor_operation_type.COPY_FILES:
      for d in affected_dirs:
        if path.exists(d) and dir_util.is_empty(d):
          dir_util.remove(d)
    return operation_items

  @classmethod
  def _make_dst_filename(clazz,
                         operation,
                         filename,
                         src_pattern,
                         dst_pattern,
                         copy_dirs,
                         word_boundary,
                         word_boundary_chars):
    assert isinstance(operation, refactor_operation_type)

    if operation == refactor_operation_type.RENAME_DIRS:
      basename = path.basename(filename)
      dirname = path.dirname(filename)
      replaced_dirname = bf_path.replace_all(dirname,
                                             src_pattern,
                                             dst_pattern,
                                             word_boundary = word_boundary,
                                             word_boundary_chars = word_boundary_chars)
      return path.join(replaced_dirname, basename)
    elif operation == refactor_operation_type.RENAME_FILES or copy_dirs:
      return bf_path.replace_all(filename,
                                 src_pattern,
                                 dst_pattern,
                                 word_boundary = word_boundary,
                                 word_boundary_chars = word_boundary_chars)
    elif operation == refactor_operation_type.COPY_FILES:
      basename = path.basename(filename)
      dirname = path.dirname(filename)
      replaced_basename = bf_path.replace_all(basename,
                                              src_pattern,
                                              dst_pattern,
                                              word_boundary = word_boundary,
                                              word_boundary_chars = word_boundary_chars)
      return path.join(dirname, replaced_basename)
        
  @classmethod
  def _make_operation_items(clazz,
                            operation,
                            resolved_files,
                            src_pattern,
                            dst_pattern,
                            copy_dirs,
                            word_boundary,
                            word_boundary_chars):
    operation_items = []
    affected_dirs = []
    for f in resolved_files:
      src_filename_rel = f.filename
      dst_filename_rel = clazz._make_dst_filename(operation,
                                                  src_filename_rel,
                                                  src_pattern,
                                                  dst_pattern,
                                                  copy_dirs,
                                                  word_boundary,
                                                  word_boundary_chars)
      if src_filename_rel != dst_filename_rel:
        affected_dirs.append(clazz._affected_dir(f.root_dir, path.dirname(f.filename)))
        src_filename_abs = path.join(f.root_dir, src_filename_rel)
        dst_filename_abs = path.join(f.root_dir, dst_filename_rel)
        item = refactor_item(src_filename_abs, dst_filename_abs)
        operation_items.append(item)
    affected_dirs = sorted(algorithm.unique(affected_dirs))
    decomposed_affected_items = []
    for f in affected_dirs:
      next_paths = bf_path.decompose(path.sep + f.dirname)
      for next_path in next_paths:
        item = clazz._affected_dir(f.root_dir, file_util.lstrip_sep(next_path))
        decomposed_affected_items.append(item)
    decomposed_affected_items = sorted(decomposed_affected_items, key = lambda item: bf_path.depth(item.dirname), reverse = True)
    decomposed_affected_dirs = [ path.join(item.root_dir, item.dirname) for item in decomposed_affected_items ]
    return operation_items, decomposed_affected_dirs

  @classmethod
  def search_files(clazz, filenames, text, options = None):
    'Return only the text files in filesnames.'
    options = options or refactor_options()
    result = []
    for filename in filenames:
      result += file_search.search_file(filename,
                                        text,
                                        word_boundary = options.word_boundary,
                                        word_boundary_chars = options.word_boundary_chars)
    return result

  @classmethod
  def match_files(clazz, filenames, text, options = None):
    options = options or refactor_options()
    search_rv = clazz.search_files(filenames, text, options = options)
    return algorithm.unique([ s.filename for s in search_rv ])
      
  @classmethod
  def reindent_files(clazz, files, indent, backup):
    check.check_string_seq(files)
    check.check_int(indent)
    check.check_bool(backup)

    clazz._log.log_method_d()

    python_files = clazz.resolve_python_files(files)
    for filename in python_files:
      refactor_reindent.reindent_file(filename, indent, backup)
