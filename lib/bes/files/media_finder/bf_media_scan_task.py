#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import time

from bes.files.bf_filename import bf_filename
from bes.files.find.bf_file_scanner import bf_file_scanner
from bes.files.find.bf_file_scanner_options import bf_file_scanner_options
from bes.files.mime.bf_mime import bf_mime
from bes.files.mime.bf_mime_type_detector import bf_mime_type_detector
from bes.system.log import logger, log as _log_class

from .bf_media_file_entry import bf_media_file_entry
from .bf_media_scan_status import bf_media_scan_status

_log = logger('bf_media_scan')

def bf_media_scan_task(context, args):
  root_dirs         = args['root_dirs']
  media_types       = args['media_types']             # frozenset of 'image', 'video', 'audio'
  ignore_filename   = args.get('ignore_filename')     # str | None
  chunk_size        = args.get('chunk_size', 50)      # from options.scan_chunk_size
  ignore_extensions = args.get('ignore_extensions') or frozenset()
  file_matcher      = args.get('file_matcher')        # bf_file_matcher | None

  scanner_kwargs = {
    'include_empty_files': False,
  }
  if ignore_filename:
    scanner_kwargs['ignore_filename'] = ignore_filename
  options = bf_file_scanner_options(**scanner_kwargs)
  scanner = bf_file_scanner(options=options)

  _measuring = _log_class.get_tag_level('bf_media_scan') <= _log_class.DEBUG
  _scan_start = time.monotonic() if _measuring else 0.0
  _mime_time  = 0.0

  batch = []
  found         = 0
  media_matched = 0
  scanned       = 0

  for entry in scanner.scan_gen(root_dirs):
    context.raise_cancelled_if_needed('scan cancelled')

    filename = entry.filename
    basename = path.basename(filename)

    if ignore_extensions and bf_filename.has_any_extension(basename, list(ignore_extensions), ignore_case=True):
      scanned += 1
      continue

    ext = (bf_filename.extension(filename) or '').lower()

    # Tier 1: mime detection
    if _measuring:
      _t0 = time.monotonic()
    try:
      mime_type = bf_mime_type_detector.detect_mime_type(filename)
    except Exception:
      if _measuring:
        _mime_time += time.monotonic() - _t0
      scanned += 1
      continue
    if _measuring:
      _mime_time += time.monotonic() - _t0

    media_type = bf_mime.media_type_for_mime_type(mime_type)

    scanned += 1

    if media_type not in media_types:
      continue

    media_matched += 1

    if file_matcher and not file_matcher.match(entry):
      continue

    try:
      st    = entry.stat
      size  = st.st_size
      mtime = st.st_mtime
    except OSError:
      continue

    found += 1
    batch.append(bf_media_file_entry(
      root_dir   = entry.root_dir,
      filename   = filename,
      size       = size,
      mtime      = mtime,
      extension  = ext,
      mime_type  = mime_type,
      media_type = media_type,
    ))

    if len(batch) >= chunk_size:
      context.report_status(bf_media_scan_status(entries=batch[:], found=found,
                                                  media_matched=media_matched, scanned=scanned))
      batch.clear()

  if batch:
    context.report_status(bf_media_scan_status(entries=batch, found=found,
                                                media_matched=media_matched, scanned=scanned))

  if _measuring:
    total = time.monotonic() - _scan_start
    pct   = 100 * _mime_time / total if total > 0 else 0
    _log.log_d(f'scan done: {scanned} files in {total:.3f}s | mime {_mime_time:.3f}s ({pct:.0f}%) | non-mime {total - _mime_time:.3f}s')

  return {'found': found, 'media_matched': media_matched, 'scanned': scanned}
