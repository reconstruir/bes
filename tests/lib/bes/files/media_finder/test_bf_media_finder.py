#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import time
from collections import namedtuple

from bes.testing.unit_test import unit_test
from bes.btask.btask_processor import btask_processor
from bes.files.media_finder.bf_media_finder import bf_media_finder
from bes.files.media_finder.bf_media_finder_callbacks import bf_media_finder_callbacks
from bes.files.media_finder.bf_media_finder_options import bf_media_finder_options
from bes.files.media_finder.bf_media_finder_state import bf_media_finder_state
from bes.files.media_finder.bf_media_sort_type import bf_media_sort_type

from _bes_unit_test_common.unit_test_media import unit_test_media

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

  def test_sort_slow_raises(self):
    'Slow sort types raise NotImplementedError until Tier 2 is implemented.'
    tmp = self._make_dir({'a.jpg': self.JPG})
    processor = btask_processor('test', num_processes=2)
    self.addCleanup(processor.stop)
    finder = bf_media_finder(processor)
    errors = []

    cbs = bf_media_finder_callbacks(on_error=lambda e: errors.append(e))
    finder.scan([tmp], options=bf_media_finder_options(sort_type='resolution'), callbacks=cbs)
    finder.run()
    self.assertEqual(1, len(errors))
    self.assertIsInstance(errors[0], NotImplementedError)

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

if __name__ == '__main__':
  unit_test.main()
