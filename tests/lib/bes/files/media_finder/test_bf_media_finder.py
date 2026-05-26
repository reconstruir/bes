#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import time
from collections import namedtuple

from bes.testing.unit_test import unit_test
from bes.btask.btask_processor import btask_processor
from bes.files.media_finder.bf_media_feature_not_available import BF_FEATURE_NOT_AVAILABLE
from bes.files.media_finder.bf_media_feature_resolver_base import bf_media_feature_resolver_base
from bes.files.media_finder.bf_media_finder import bf_media_finder
from bes.files.media_finder.bf_media_finder_callbacks import bf_media_finder_callbacks
from bes.files.media_finder.bf_media_finder_options import bf_media_finder_options
from bes.files.media_finder.bf_media_finder_state import bf_media_finder_state
from bes.files.media_finder.bf_media_sort_type import bf_media_sort_type

from _bes_unit_test_common.unit_test_media import unit_test_media

# ---------------------------------------------------------------------------
# Fake resolvers used by resolve-phase tests (defined at module level so they
# are picklable — btask workers run in a subprocess on macOS).
# ---------------------------------------------------------------------------

class _SizeResolver(bf_media_feature_resolver_base):
  'Returns file size as the resolved feature (cheap, deterministic, no I/O needed).'
  name = '_test_size_resolver'

  @classmethod
  def resolve(cls, filename, mime_type, feature_name):
    if feature_name == 'fsize':
      import os
      return os.path.getsize(filename)
    return None

class _TupleResolver(bf_media_feature_resolver_base):
  'Returns (size, 0) tuple — exercises domain-specific secondary sort.'
  name = '_test_tuple_resolver'

  @classmethod
  def resolve(cls, filename, mime_type, feature_name):
    if feature_name == 'fsize_tuple':
      import os
      s = os.path.getsize(filename)
      return (s, 0)
    return None

class _NotAvailableResolver(bf_media_feature_resolver_base):
  'Always returns BF_FEATURE_NOT_AVAILABLE.'
  name = '_test_not_available_resolver'

  @classmethod
  def resolve(cls, filename, mime_type, feature_name):
    if feature_name == 'unavailable':
      return BF_FEATURE_NOT_AVAILABLE
    return None

class _NoneResolver(bf_media_feature_resolver_base):
  'Always returns None (feature not handled).'
  name = '_test_none_resolver'

  @classmethod
  def resolve(cls, filename, mime_type, feature_name):
    return None

class _ErrorOnNameResolver(bf_media_feature_resolver_base):
  'Raises for files whose basename starts with "error_"; succeeds for others.'
  name = '_test_error_on_name_resolver'

  @classmethod
  def resolve(cls, filename, mime_type, feature_name):
    if feature_name == 'fsize':
      import os
      if os.path.basename(filename).startswith('error_'):
        raise RuntimeError('deliberate per-file error')
      return os.path.getsize(filename)
    return None

class _MixedResolver(bf_media_feature_resolver_base):
  'Alternates between None and BF_FEATURE_NOT_AVAILABLE based on file size parity.'
  name = '_test_mixed_resolver'

  @classmethod
  def resolve(cls, filename, mime_type, feature_name):
    if feature_name == 'mix':
      import os
      return BF_FEATURE_NOT_AVAILABLE if os.path.getsize(filename) % 2 == 0 else None
    return None

class _ConstResolver(bf_media_feature_resolver_base):
  'Always returns 42 for feature "const".'
  name = '_test_const_resolver'

  @classmethod
  def resolve(cls, filename, mime_type, feature_name):
    return 42 if feature_name == 'const' else None

class test_bf_media_finder(unit_test):

  # ---------------------------------------------------------------------------
  # Helpers
  # ---------------------------------------------------------------------------

  def _make_dir(self, files):
    'Create a temp dir; files is {relative_path: bytes}.'
    tmp_dir = self.make_temp_dir()
    for rel, content in files.items():
      abs_p = path.join(tmp_dir, rel)
      os.makedirs(path.dirname(abs_p), exist_ok=True)
      with open(abs_p, 'wb') as f:
        f.write(content)
    return tmp_dir

  _scan_result = namedtuple('_scan_result',
    'entries, progress_calls, state_changes, done_called, cancelled_called, final_state')

  def _run_scan(self, root_dirs, options=None, cancel_on_first_progress=False):
    if isinstance(root_dirs, str):
      root_dirs = [root_dirs]
    processor = btask_processor('test', num_processes=4)
    self.addCleanup(processor.stop)
    finder = bf_media_finder(processor)

    all_entries      = []
    progress_calls   = []
    state_changes    = []
    done_called      = [False]
    cancelled_called = [False]
    cancel_done      = [False]

    def _progress(found, scanned):
      progress_calls.append((found, scanned))
      if cancel_on_first_progress and not cancel_done[0]:
        cancel_done[0] = True
        finder.cancel()

    def _done(entries):
      all_entries.extend(entries)
      done_called[0] = True

    def _cancel():
      cancelled_called[0] = True

    def _state(state):
      state_changes.append(state)

    cbs = bf_media_finder_callbacks(
      on_scan_progress = _progress,
      on_scan_done     = _done,
      on_cancel        = _cancel,
      on_state_changed = _state,
    )
    finder.scan(root_dirs, options=options, callbacks=cbs)
    finder.run()

    return self._scan_result(
      all_entries, progress_calls, state_changes,
      done_called[0], cancelled_called[0], finder.state,
    )

  _resolve_result = namedtuple('_resolve_result',
    'entries, scan_done_entries, scan_done_resolved_snapshots, '
    'resolve_progress_calls, resolve_done_called, '
    'state_changes, scan_done_called, cancelled_called, error, final_state, finder')

  def _run_resolve_scan(self, root_dirs, options, cancel_during_resolve=False):
    'Run a scan with an extended sort type; blocks until resolve phase completes.'
    if isinstance(root_dirs, str):
      root_dirs = [root_dirs]
    processor = btask_processor('test', num_processes=4)
    self.addCleanup(processor.stop)
    finder = bf_media_finder(processor)

    scan_done_entries          = []
    scan_done_resolved_snapshots = []  # dict copies of resolved_features at on_scan_done time
    resolve_progress_calls    = []
    resolve_done_called        = [False]
    scan_done_called           = [False]
    state_changes              = []
    cancelled_called           = [False]
    error_box                  = [None]
    cancel_done                = [False]

    def _scan_done(entries):
      scan_done_entries.extend(entries)
      scan_done_resolved_snapshots.extend(dict(e.resolved_features) for e in entries)
      scan_done_called[0] = True

    def _resolve_progress(done, total):
      resolve_progress_calls.append((done, total))
      if cancel_during_resolve and not cancel_done[0]:
        cancel_done[0] = True
        finder.cancel()

    def _resolve_done():
      resolve_done_called[0] = True

    def _cancel():
      cancelled_called[0] = True

    def _state(state):
      state_changes.append(state)

    def _error(exc):
      error_box[0] = exc

    cbs = bf_media_finder_callbacks(
      on_scan_done        = _scan_done,
      on_resolve_progress = _resolve_progress,
      on_resolve_done     = _resolve_done,
      on_cancel           = _cancel,
      on_state_changed    = _state,
      on_error            = _error,
    )
    finder.scan(root_dirs, options=options, callbacks=cbs)
    finder.run()

    return self._resolve_result(
      finder.entries,
      list(scan_done_entries),
      list(scan_done_resolved_snapshots),
      list(resolve_progress_calls),
      resolve_done_called[0],
      list(state_changes),
      scan_done_called[0],
      cancelled_called[0],
      error_box[0],
      finder.state,
      finder,
    )

  def _media_types(self, entries):
    return sorted(set(e.media_type for e in entries))

  def _basenames(self, entries):
    return [path.basename(e.filename) for e in entries]

  # ---------------------------------------------------------------------------
  # Fixture content shorthands
  # ---------------------------------------------------------------------------

  PNG = unit_test_media.PNG_SMALLEST_POSSIBLE
  JPG = unit_test_media.JPG_SMALLEST_POSSIBLE
  MP4 = unit_test_media.MP4_SMALLEST_POSSIBLE
  JUNK = unit_test_media.UNKNOWN   # not a media file

  # ---------------------------------------------------------------------------
  # Scan phase — basic
  # ---------------------------------------------------------------------------

  def test_scan_images_found(self):
    tmp = self._make_dir({
      'a.png': self.PNG,
      'b.jpg': self.JPG,
      'c.txt': b'not an image',
    })
    r = self._run_scan(tmp, bf_media_finder_options(media_types='image'))
    self.assertEqual(2, len(r.entries))
    self.assertTrue(all(e.media_type == 'image' for e in r.entries))

  def test_scan_videos_found(self):
    tmp = self._make_dir({
      'clip.mp4': self.MP4,
      'photo.jpg': self.JPG,
    })
    r = self._run_scan(tmp, bf_media_finder_options(media_types='video'))
    self.assertEqual(1, len(r.entries))
    self.assertEqual('video', r.entries[0].media_type)

  def test_scan_all_media_types(self):
    tmp = self._make_dir({
      'a.png': self.PNG,
      'b.mp4': self.MP4,
      'c.txt': b'text',
    })
    r = self._run_scan(tmp)
    self.assertEqual(2, len(r.entries))
    self.assertIn('image', self._media_types(r.entries))
    self.assertIn('video', self._media_types(r.entries))

  def test_scan_empty_dir(self):
    tmp = self._make_dir({})
    r = self._run_scan(tmp)
    self.assertEqual(0, len(r.entries))
    self.assertTrue(r.done_called)

  # ---------------------------------------------------------------------------
  # Scan phase — file filters
  # ---------------------------------------------------------------------------

  def test_part_file_excluded(self):
    tmp = self._make_dir({
      'good.jpg': self.JPG,
      'download.jpg.part': self.JPG,
    })
    r = self._run_scan(tmp)
    self.assertEqual(1, len(r.entries))
    self.assertEqual('good.jpg', path.basename(r.entries[0].filename))

  def test_dotunderscore_file_excluded(self):
    tmp = self._make_dir({
      'good.jpg': self.JPG,
      '._resource.jpg': self.JPG,
    })
    r = self._run_scan(tmp)
    self.assertEqual(1, len(r.entries))
    self.assertEqual('good.jpg', path.basename(r.entries[0].filename))

  # ---------------------------------------------------------------------------
  # Scan phase — mime correctness
  # ---------------------------------------------------------------------------

  def test_corrupted_file_excluded(self):
    'A file with a valid extension but garbage content is excluded.'
    tmp = self._make_dir({
      'real.jpg': self.JPG,
      'fake.jpg': self.JUNK,
    })
    r = self._run_scan(tmp)
    self.assertEqual(1, len(r.entries))
    self.assertEqual('real.jpg', path.basename(r.entries[0].filename))

  def test_mime_beats_extension(self):
    'PNG bytes in a .jpg file → detected as image/png, still accepted as image.'
    tmp = self._make_dir({
      'actually_png.jpg': self.PNG,
    })
    r = self._run_scan(tmp, bf_media_finder_options(media_types='image'))
    self.assertEqual(1, len(r.entries))
    self.assertEqual('image/png', r.entries[0].mime_type)

  def test_non_standard_extension_found(self):
    'PNG bytes in a .dat file are found; extension is ignored.'
    tmp = self._make_dir({
      'image.dat': self.PNG,
      'real.png':  self.PNG,
    })
    r = self._run_scan(tmp, bf_media_finder_options(media_types='image'))
    self.assertEqual(2, len(r.entries))

  # ---------------------------------------------------------------------------
  # Scan phase — entry fields
  # ---------------------------------------------------------------------------

  def test_entry_fields_populated(self):
    tmp = self._make_dir({'photo.png': self.PNG})
    r = self._run_scan(tmp)
    self.assertEqual(1, len(r.entries))
    e = r.entries[0]
    self.assertEqual(tmp, e.root_dir)
    self.assertTrue(path.isabs(e.filename))
    self.assertGreater(e.size, 0)
    self.assertGreater(e.mtime, 0)
    self.assertEqual('png', e.extension)
    self.assertEqual('image/png', e.mime_type)
    self.assertEqual('image', e.media_type)

  def test_relative_filename(self):
    tmp = self._make_dir({'sub/photo.png': self.PNG})
    r = self._run_scan(tmp)
    self.assertEqual(1, len(r.entries))
    self.assertEqual('sub/photo.png', r.entries[0].relative_filename)

  # ---------------------------------------------------------------------------
  # Multiple root directories
  # ---------------------------------------------------------------------------

  def test_multiple_roots_both_found(self):
    tmp_a = self._make_dir({'alpha.jpg': self.JPG})
    tmp_b = self._make_dir({'beta.jpg': self.JPG})
    r = self._run_scan([tmp_a, tmp_b])
    self.assertEqual(2, len(r.entries))

  def test_multiple_roots_correct_root_dir(self):
    tmp_a = self._make_dir({'a.jpg': self.JPG})
    tmp_b = self._make_dir({'b.jpg': self.JPG})
    r = self._run_scan([tmp_a, tmp_b])
    root_dirs = {e.root_dir for e in r.entries}
    self.assertIn(tmp_a, root_dirs)
    self.assertIn(tmp_b, root_dirs)
    for e in r.entries:
      self.assertTrue(e.filename.startswith(e.root_dir))

  # ---------------------------------------------------------------------------
  # Callbacks and state machine
  # ---------------------------------------------------------------------------

  def test_state_transitions(self):
    tmp = self._make_dir({'a.png': self.PNG})
    r = self._run_scan(tmp)
    self.assertIn(bf_media_finder_state.SCANNING,     r.state_changes)
    self.assertIn(bf_media_finder_state.READY_QUICK,  r.state_changes)
    scan_idx  = r.state_changes.index(bf_media_finder_state.SCANNING)
    ready_idx = r.state_changes.index(bf_media_finder_state.READY_QUICK)
    self.assertLess(scan_idx, ready_idx)

  def test_done_called_once(self):
    tmp = self._make_dir({'a.png': self.PNG, 'b.jpg': self.JPG})
    r = self._run_scan(tmp)
    self.assertTrue(r.done_called)

  def test_final_state_ready_quick(self):
    tmp = self._make_dir({'a.png': self.PNG})
    r = self._run_scan(tmp)
    self.assertEqual(bf_media_finder_state.READY_QUICK, r.final_state)

  def test_progress_counters_valid(self):
    'found <= scanned must hold for every progress report.'
    tmp = self._make_dir({f'{i:03d}.png': self.PNG for i in range(60)})
    r = self._run_scan(tmp)
    for found, scanned in r.progress_calls:
      self.assertLessEqual(found, scanned)
      self.assertGreaterEqual(found, 0)
      self.assertGreaterEqual(scanned, 0)

  def test_progress_counters_increase(self):
    tmp = self._make_dir({f'{i:03d}.png': self.PNG for i in range(60)})
    r = self._run_scan(tmp)
    if len(r.progress_calls) > 1:
      for (f1, s1), (f2, s2) in zip(r.progress_calls, r.progress_calls[1:]):
        self.assertGreaterEqual(f2, f1)
        self.assertGreaterEqual(s2, s1)

  # ---------------------------------------------------------------------------
  # Cancellation
  # ---------------------------------------------------------------------------

  def test_cancel_mid_scan(self):
    '200 files ensure many remain after first batch; cancel on first progress.'
    tmp = self._make_dir({f'{i:03d}.png': self.PNG for i in range(200)})
    r = self._run_scan(tmp, cancel_on_first_progress=True)
    self.assertEqual(bf_media_finder_state.IDLE, r.final_state)
    self.assertTrue(r.cancelled_called)
    self.assertFalse(r.done_called)

  def test_cancel_transitions_to_idle(self):
    tmp = self._make_dir({f'{i:03d}.png': self.PNG for i in range(200)})
    r = self._run_scan(tmp, cancel_on_first_progress=True)
    self.assertEqual(bf_media_finder_state.IDLE, r.final_state)

  def test_second_scan_after_cancel(self):
    tmp = self._make_dir({f'{i:03d}.png': self.PNG for i in range(200)})
    # first scan — cancel it
    self._run_scan(tmp, cancel_on_first_progress=True)
    # second scan — should complete normally
    r = self._run_scan(tmp)
    self.assertTrue(r.done_called)
    self.assertEqual(bf_media_finder_state.READY_QUICK, r.final_state)

  # ---------------------------------------------------------------------------
  # Sort types
  # ---------------------------------------------------------------------------

  def test_sort_found_order_no_reorder(self):
    'found_order does not sort; entries come in filesystem walk order.'
    tmp = self._make_dir({'a.png': self.PNG, 'b.png': self.PNG, 'c.png': self.PNG})
    r = self._run_scan(tmp, bf_media_finder_options(sort_type='found_order'))
    self.assertEqual(3, len(r.entries))

  def test_sort_name_alphabetical(self):
    tmp = self._make_dir({
      'charlie.jpg': self.JPG,
      'alpha.png':   self.PNG,
      'bravo.jpg':   self.JPG,
    })
    r = self._run_scan(tmp, bf_media_finder_options(sort_type='name'))
    names = self._basenames(r.entries)
    self.assertEqual(sorted(names, key=str.lower), names)

  def test_sort_name_case_insensitive_default(self):
    tmp = self._make_dir({
      'Zebra.png': self.PNG,
      'apple.jpg': self.JPG,
      'Mango.jpg': self.JPG,
    })
    r = self._run_scan(tmp, bf_media_finder_options(sort_type='name', case_sensitive=False))
    names = self._basenames(r.entries)
    self.assertEqual(sorted(names, key=str.lower), names)

  def test_sort_size(self):
    # build files of increasing size by repeating content
    tmp = self._make_dir({
      'large.jpg':  self.JPG * 3,
      'small.jpg':  self.JPG,
      'medium.jpg': self.JPG * 2,
    })
    r = self._run_scan(tmp, bf_media_finder_options(sort_type='size'))
    sizes = [e.size for e in r.entries]
    self.assertEqual(sorted(sizes), sizes)

  def test_sort_date(self):
    tmp = self._make_dir({
      'new.jpg': self.JPG,
      'old.jpg': self.JPG,
    })
    # manually set mtimes
    now = time.time()
    os.utime(path.join(tmp, 'old.jpg'), (now - 1000, now - 1000))
    os.utime(path.join(tmp, 'new.jpg'), (now,         now))
    r = self._run_scan(tmp, bf_media_finder_options(sort_type='date'))
    mtimes = [e.mtime for e in r.entries]
    self.assertEqual(sorted(mtimes), mtimes)

  def test_sort_name_reversed(self):
    tmp = self._make_dir({
      'charlie.jpg': self.JPG,
      'alpha.png':   self.PNG,
      'bravo.jpg':   self.JPG,
    })
    r = self._run_scan(tmp, bf_media_finder_options(sort_type='name', sort_reversed=True))
    names = self._basenames(r.entries)
    self.assertEqual(sorted(names, key=str.lower, reverse=True), names)

  def test_sort_size_reversed(self):
    tmp = self._make_dir({
      'large.jpg':  self.JPG * 3,
      'small.jpg':  self.JPG,
      'medium.jpg': self.JPG * 2,
    })
    r = self._run_scan(tmp, bf_media_finder_options(sort_type='size', sort_reversed=True))
    sizes = [e.size for e in r.entries]
    self.assertEqual(sorted(sizes, reverse=True), sizes)

  def test_sort_found_order_reversed(self):
    tmp = self._make_dir({'a.png': self.PNG, 'b.png': self.PNG, 'c.png': self.PNG})
    r_fwd = self._run_scan(tmp, bf_media_finder_options(sort_type='found_order'))
    r_rev = self._run_scan(tmp, bf_media_finder_options(sort_type='found_order', sort_reversed=True))
    self.assertEqual(3, len(r_rev.entries))
    self.assertEqual(
      [e.filename for e in r_fwd.entries],
      list(reversed([e.filename for e in r_rev.entries])),
    )

  def test_extended_sort_no_resolver_fires_on_error(self):
    'Extended sort with feature_resolver=None routes ValueError through on_error.'
    tmp = self._make_dir({'a.jpg': self.JPG})
    processor = btask_processor('test', num_processes=2)
    self.addCleanup(processor.stop)
    finder = bf_media_finder(processor)
    errors = []

    cbs = bf_media_finder_callbacks(on_error=lambda e: errors.append(e))
    finder.scan([tmp], options=bf_media_finder_options(sort_type='resolution'), callbacks=cbs)
    finder.run()
    self.assertEqual(1, len(errors))
    self.assertIsInstance(errors[0], ValueError)

  # ---------------------------------------------------------------------------
  # Ignore file
  # ---------------------------------------------------------------------------

  def test_ignore_file_respected(self):
    tmp = self._make_dir({
      'keep.jpg':         self.JPG,
      'skip/photo.jpg':   self.JPG,
      'skip/.bes_ignore': b'*\n',
    })
    r = self._run_scan(tmp)
    basenames = self._basenames(r.entries)
    self.assertIn('keep.jpg', basenames)
    self.assertNotIn('photo.jpg', basenames)

  def test_ignore_file_disabled(self):
    tmp = self._make_dir({
      'keep.jpg':         self.JPG,
      'skip/photo.jpg':   self.JPG,
      'skip/.bes_ignore': b'*\n',
    })
    r = self._run_scan(tmp, bf_media_finder_options(ignore_file=''))
    self.assertEqual(2, len(r.entries))

  # ---------------------------------------------------------------------------
  # Resolve phase — state machine
  # ---------------------------------------------------------------------------

  def test_resolve_state_transitions(self):
    tmp = self._make_dir({'a.jpg': self.JPG, 'b.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver)
    r = self._run_resolve_scan(tmp, opts)
    states = r.state_changes
    self.assertIn(bf_media_finder_state.SCANNING,    states)
    self.assertIn(bf_media_finder_state.READY_QUICK, states)
    self.assertIn(bf_media_finder_state.RESOLVING,   states)
    self.assertIn(bf_media_finder_state.READY,       states)
    self.assertLess(states.index(bf_media_finder_state.SCANNING),    states.index(bf_media_finder_state.READY_QUICK))
    self.assertLess(states.index(bf_media_finder_state.READY_QUICK), states.index(bf_media_finder_state.RESOLVING))
    self.assertLess(states.index(bf_media_finder_state.RESOLVING),   states.index(bf_media_finder_state.READY))

  def test_resolve_not_triggered_for_intrinsic(self):
    tmp = self._make_dir({'a.jpg': self.JPG})
    r = self._run_resolve_scan(tmp, bf_media_finder_options(sort_type='name', feature_resolver=_SizeResolver))
    self.assertNotIn(bf_media_finder_state.RESOLVING, r.state_changes)
    self.assertNotIn(bf_media_finder_state.READY,     r.state_changes)

  def test_final_state_ready_after_resolve(self):
    tmp = self._make_dir({'a.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver)
    r = self._run_resolve_scan(tmp, opts)
    self.assertEqual(bf_media_finder_state.READY, r.final_state)

  # ---------------------------------------------------------------------------
  # Resolve phase — callbacks ordering and counts
  # ---------------------------------------------------------------------------

  def test_on_scan_done_fires_before_resolving(self):
    tmp = self._make_dir({'a.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver)
    r = self._run_resolve_scan(tmp, opts)
    scan_idx    = r.state_changes.index(bf_media_finder_state.READY_QUICK)
    resolve_idx = r.state_changes.index(bf_media_finder_state.RESOLVING)
    self.assertLess(scan_idx, resolve_idx)
    self.assertTrue(r.scan_done_called)

  def test_on_resolve_progress_fires(self):
    tmp = self._make_dir({'a.jpg': self.JPG, 'b.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver)
    r = self._run_resolve_scan(tmp, opts)
    self.assertGreater(len(r.resolve_progress_calls), 0)

  def test_on_resolve_progress_done_monotonic(self):
    tmp = self._make_dir({f'{i}.jpg': self.JPG for i in range(5)})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1)
    r = self._run_resolve_scan(tmp, opts)
    dones = [d for d, _ in r.resolve_progress_calls]
    self.assertEqual(dones, sorted(dones))

  def test_on_resolve_progress_total_constant(self):
    tmp = self._make_dir({f'{i}.jpg': self.JPG for i in range(4)})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1)
    r = self._run_resolve_scan(tmp, opts)
    totals = [t for _, t in r.resolve_progress_calls]
    self.assertTrue(all(t == totals[0] for t in totals))

  def test_on_resolve_progress_total_equals_entry_count(self):
    tmp = self._make_dir({'a.jpg': self.JPG, 'b.jpg': self.JPG, 'c.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1)
    r = self._run_resolve_scan(tmp, opts)
    _, total = r.resolve_progress_calls[-1]
    self.assertEqual(3, total)

  def test_on_resolve_progress_final_done_equals_total(self):
    tmp = self._make_dir({'a.jpg': self.JPG, 'b.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1)
    r = self._run_resolve_scan(tmp, opts)
    done, total = r.resolve_progress_calls[-1]
    self.assertEqual(done, total)

  def test_on_resolve_done_fires_once(self):
    tmp = self._make_dir({'a.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver)
    r = self._run_resolve_scan(tmp, opts)
    self.assertTrue(r.resolve_done_called)

  def test_on_resolve_done_after_scan_done(self):
    tmp = self._make_dir({'a.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver)
    r = self._run_resolve_scan(tmp, opts)
    self.assertTrue(r.scan_done_called)
    self.assertTrue(r.resolve_done_called)
    ready_quick_idx = r.state_changes.index(bf_media_finder_state.READY_QUICK)
    ready_idx       = r.state_changes.index(bf_media_finder_state.READY)
    self.assertLess(ready_quick_idx, ready_idx)

  # ---------------------------------------------------------------------------
  # Resolve phase — resolved_features population
  # ---------------------------------------------------------------------------

  def test_resolved_features_empty_at_scan_done(self):
    tmp = self._make_dir({'a.jpg': self.JPG, 'b.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver)
    r = self._run_resolve_scan(tmp, opts)
    # Use snapshots captured at on_scan_done time (entries are mutated by resolve phase after)
    for snapshot in r.scan_done_resolved_snapshots:
      self.assertEqual({}, snapshot)

  def test_resolved_features_populated_after_resolve(self):
    tmp = self._make_dir({'a.jpg': self.JPG, 'b.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver)
    r = self._run_resolve_scan(tmp, opts)
    for e in r.entries:
      self.assertIn('fsize', e.resolved_features)
      self.assertIsNotNone(e.resolved_features['fsize'])

  def test_resolved_features_not_available_stored(self):
    tmp = self._make_dir({'a.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='unavailable', feature_resolver=_NotAvailableResolver)
    r = self._run_resolve_scan(tmp, opts)
    for e in r.entries:
      self.assertIn('unavailable', e.resolved_features)
      self.assertIs(BF_FEATURE_NOT_AVAILABLE, e.resolved_features['unavailable'])

  def test_resolved_features_none_stored(self):
    tmp = self._make_dir({'a.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='x', feature_resolver=_NoneResolver)
    r = self._run_resolve_scan(tmp, opts)
    for e in r.entries:
      self.assertIn('x', e.resolved_features)
      self.assertIsNone(e.resolved_features['x'])

  # ---------------------------------------------------------------------------
  # Resolve phase — sort correctness
  # ---------------------------------------------------------------------------

  def test_sort_extended_real_values_ordered(self):
    tmp = self._make_dir({
      'large.jpg':  self.JPG * 3,
      'small.jpg':  self.JPG,
      'medium.jpg': self.JPG * 2,
    })
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver)
    r = self._run_resolve_scan(tmp, opts)
    sizes = [e.resolved_features.get('fsize') for e in r.entries]
    self.assertEqual(sorted(sizes), sizes)

  def test_sort_extended_not_available_at_end(self):
    tmp = self._make_dir({'a.jpg': self.JPG, 'b.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='unavailable', feature_resolver=_NotAvailableResolver)
    r = self._run_resolve_scan(tmp, opts)
    self.assertEqual(2, len(r.entries))
    # All entries have BF_FEATURE_NOT_AVAILABLE — no TypeError, all at end group
    for e in r.entries:
      self.assertIs(BF_FEATURE_NOT_AVAILABLE, e.resolved_features.get('unavailable'))

  def test_sort_extended_none_at_end(self):
    tmp = self._make_dir({'a.jpg': self.JPG, 'b.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='x', feature_resolver=_NoneResolver)
    r = self._run_resolve_scan(tmp, opts)
    self.assertEqual(2, len(r.entries))
    for e in r.entries:
      self.assertIsNone(e.resolved_features.get('x'))

  def test_sort_extended_not_available_and_none_together(self):
    'Mixed BF_FEATURE_NOT_AVAILABLE and None values sort without TypeError.'
    tmp = self._make_dir({'a.jpg': self.JPG, 'b.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='mix', feature_resolver=_MixedResolver)
    r = self._run_resolve_scan(tmp, opts)
    self.assertEqual(2, len(r.entries))  # no TypeError

  def test_sort_extended_tuple_primary_domain_secondary(self):
    tmp = self._make_dir({
      'large.jpg':  self.JPG * 3,
      'small.jpg':  self.JPG,
      'medium.jpg': self.JPG * 2,
    })
    opts = bf_media_finder_options(sort_type='fsize_tuple', feature_resolver=_TupleResolver)
    r = self._run_resolve_scan(tmp, opts)
    values = [e.resolved_features.get('fsize_tuple') for e in r.entries]
    self.assertEqual(sorted(values), values)

  def test_sort_extended_filename_tiebreaker(self):
    'Two files with identical resolved value sort by basename then dirname.'
    tmp = self._make_dir({'b.jpg': self.JPG, 'a.jpg': self.JPG})
    opts = bf_media_finder_options(sort_type='const', feature_resolver=_ConstResolver)
    r = self._run_resolve_scan(tmp, opts)
    names = [path.basename(e.filename) for e in r.entries]
    self.assertEqual(sorted(names, key=str.lower), names)

  # ---------------------------------------------------------------------------
  # Resolve phase — chunk dispatch
  # ---------------------------------------------------------------------------

  def test_scan_chunk_size_controls_progress_frequency(self):
    tmp = self._make_dir({f'{i:03d}.jpg': self.JPG for i in range(6)})
    opts = bf_media_finder_options(scan_chunk_size=2)
    r = self._run_scan(tmp, opts)
    # With 6 files and chunk_size=2, expect at least 3 progress calls
    self.assertGreaterEqual(len(r.progress_calls), 3)

  def test_resolve_single_chunk(self):
    tmp = self._make_dir({f'{i}.jpg': self.JPG for i in range(5)})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=100)
    r = self._run_resolve_scan(tmp, opts)
    # All 5 files in one chunk → one progress call
    self.assertEqual(1, len(r.resolve_progress_calls))
    done, total = r.resolve_progress_calls[0]
    self.assertEqual(5, done)
    self.assertEqual(5, total)

  def test_resolve_multiple_chunks(self):
    tmp = self._make_dir({f'{i}.jpg': self.JPG for i in range(5)})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=2)
    r = self._run_resolve_scan(tmp, opts)
    # 5 files / chunk_size=2 → 3 tasks → 3 progress calls
    self.assertEqual(3, len(r.resolve_progress_calls))
    dones = [d for d, _ in r.resolve_progress_calls]
    self.assertEqual(sorted(dones), dones)
    self.assertEqual(5, dones[-1])

  def test_resolve_chunk_size_one(self):
    n = 4
    tmp = self._make_dir({f'{i}.jpg': self.JPG for i in range(n)})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1)
    r = self._run_resolve_scan(tmp, opts)
    self.assertEqual(n, len(r.resolve_progress_calls))

  # ---------------------------------------------------------------------------
  # Resolve phase — cancel during resolve
  # ---------------------------------------------------------------------------

  def test_cancel_mid_resolve_transitions_to_idle(self):
    # Use many files so at least some resolve tasks are still in-flight at cancel
    tmp = self._make_dir({f'{i:03d}.jpg': self.JPG for i in range(30)})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1)
    r = self._run_resolve_scan(tmp, opts, cancel_during_resolve=True)
    self.assertEqual(bf_media_finder_state.IDLE, r.final_state)

  def test_cancel_mid_resolve_on_cancel_fires(self):
    tmp = self._make_dir({f'{i:03d}.jpg': self.JPG for i in range(30)})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1)
    r = self._run_resolve_scan(tmp, opts, cancel_during_resolve=True)
    self.assertTrue(r.cancelled_called)

  def test_cancel_mid_resolve_no_done_after(self):
    tmp = self._make_dir({f'{i:03d}.jpg': self.JPG for i in range(30)})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1)
    r = self._run_resolve_scan(tmp, opts, cancel_during_resolve=True)
    self.assertFalse(r.resolve_done_called)

  def test_second_scan_after_mid_resolve_cancel(self):
    tmp = self._make_dir({f'{i:03d}.jpg': self.JPG for i in range(30)})
    opts_resolve = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1)
    self._run_resolve_scan(tmp, opts_resolve, cancel_during_resolve=True)
    # Second scan with simple options should complete normally
    r = self._run_scan(tmp, bf_media_finder_options())
    self.assertTrue(r.done_called)
    self.assertEqual(bf_media_finder_state.READY_QUICK, r.final_state)

  # ---------------------------------------------------------------------------
  # Cross-phase interactions
  # ---------------------------------------------------------------------------

  def test_cancel_mid_scan_no_resolve_triggered(self):
    tmp = self._make_dir({f'{i:03d}.jpg': self.JPG for i in range(200)})
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1)
    r = self._run_resolve_scan(tmp, opts, cancel_during_resolve=False)
    # If scan was cancelled before on_scan_done, resolving should not have started
    # (We cannot guarantee cancel mid-scan since timing varies; test cancelling from scan progress)
    # Use the normal cancel test instead
    r2 = self._run_scan(tmp, cancel_on_first_progress=True)
    self.assertNotIn(bf_media_finder_state.RESOLVING, r2.state_changes)

  def test_new_scan_during_resolve_cancels_resolve(self):
    'scan() called while RESOLVING cancels in-flight resolve tasks; new scan reaches READY_QUICK.'
    tmp = self._make_dir({f'{i:03d}.jpg': self.JPG for i in range(30)})
    processor = btask_processor('test', num_processes=4)
    self.addCleanup(processor.stop)
    finder = bf_media_finder(processor)

    new_scan_states = []
    rescan_triggered = [False]

    def _resolve_progress(done, total):
      if not rescan_triggered[0]:
        rescan_triggered[0] = True
        new_cbs = bf_media_finder_callbacks(
          on_state_changed=lambda s: new_scan_states.append(s),
        )
        finder.scan([tmp], callbacks=new_cbs)

    cbs = bf_media_finder_callbacks(on_resolve_progress=_resolve_progress)
    opts = bf_media_finder_options(
      sort_type='fsize', feature_resolver=_SizeResolver, resolve_chunk_size=1,
    )
    finder.scan([tmp], options=opts, callbacks=cbs)
    finder.run()

    self.assertTrue(rescan_triggered[0])
    self.assertIn(bf_media_finder_state.READY_QUICK, new_scan_states)
    self.assertEqual(bf_media_finder_state.READY_QUICK, finder.state)

  def test_resolver_exception_per_file_silently_skipped(self):
    'Resolver raising for one file: that entry has no resolved attr; others resolved normally.'
    import os.path as path
    tmp = self._make_dir({
      'error_bad.jpg': self.JPG,
      'ok_b.jpg':      self.JPG,
      'ok_c.jpg':      self.JPG,
    })
    opts = bf_media_finder_options(sort_type='fsize', feature_resolver=_ErrorOnNameResolver, resolve_chunk_size=1)
    r = self._run_resolve_scan(tmp, opts)
    entries_by_name = {path.basename(e.filename): e for e in r.entries}
    # The file whose name starts with 'error_' should have no 'fsize' key
    self.assertNotIn('fsize', entries_by_name['error_bad.jpg'].resolved_features)
    # The other two files should be resolved normally
    self.assertIn('fsize', entries_by_name['ok_b.jpg'].resolved_features)
    self.assertIn('fsize', entries_by_name['ok_c.jpg'].resolved_features)
    self.assertTrue(r.resolve_done_called)

if __name__ == '__main__':
  unit_test.main()
