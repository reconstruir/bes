#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import re
import string
import unicodedata

from bes.system.check import check

from .bf_filename import bf_filename

class bf_filename_simplify(object):
  'Simplify filenames: strip diacritics, lowercase, collapse whitespace and punctuation to a separator.'

  _PUNCT_SET = frozenset(string.punctuation)

  @classmethod
  def simplify(clazz, basename, separator='_'):
    '''Simplify a basename.

    Accepts a bare filename with no directory component.  Raises ValueError if
    a path separator is found or if the stem reduces to empty after simplification.
    The extension is lowercased but otherwise left unchanged.
    '''
    check.check_string(basename)
    check.check_string(separator)

    if path.sep in basename:
      raise ValueError(f'basename must not contain path separators: "{basename}"')

    ext = bf_filename.extension(basename)
    stem = bf_filename.without_extension(basename)

    new_stem = clazz.simplify_stem(stem, separator=separator)
    if not new_stem:
      raise ValueError(f'basename simplifies to an empty stem: "{basename}"')

    new_ext = ext.lower() if ext else ext
    return bf_filename.add_extension(new_stem, new_ext)

  @classmethod
  def simplify_stem(clazz, text, separator='_'):
    '''Simplify a plain string with no extension awareness.

    Pipeline:
      1. NFKD decompose; drop combining marks (Mn) — strips diacritics from
         Western chars while leaving Cyrillic, CJK, Arabic etc. intact.
      2. Lowercase.
      3. Replace whitespace and ASCII punctuation with separator.
      4. Collapse runs of separator to one.
      5. Strip leading/trailing separator.
    '''
    check.check_string(text)
    check.check_string(separator)

    result = clazz._normalize_unicode(text)
    result = result.lower()
    result = clazz._replace_whitespace_and_punctuation(result, separator)
    return result

  @classmethod
  def _normalize_unicode(clazz, s):
    decomposed = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in decomposed if unicodedata.category(c) != 'Mn')

  @classmethod
  def _replace_whitespace_and_punctuation(clazz, s, separator):
    parts = []
    for c in s:
      if c.isspace() or c in clazz._PUNCT_SET:
        parts.append(separator)
      else:
        parts.append(c)
    result = ''.join(parts)
    if separator:
      result = re.sub(re.escape(separator) + r'+', separator, result)
      result = result.strip(separator)
    return result
