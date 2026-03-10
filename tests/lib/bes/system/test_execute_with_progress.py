#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.execute import execute
from bes.testing.unit_test import unit_test

class test_execute_with_progress(unit_test):

  def test_events_collected(self):
    script = '''\
#!/usr/bin/env python
import sys
sys.stdout.write('line1\\n')
sys.stdout.flush()
sys.stdout.write('line2\\n')
sys.stdout.flush()
sys.stdout.write('line3\\n')
sys.stdout.flush()
'''
    tmp = self.make_temp_file(content=script, perm=0o0755, suffix='.py')
    def parser(stdout, stderr):
      line = (stdout or '').strip()
      return line if line else None
    rv = execute.execute_with_progress(tmp, line_parser=parser)
    self.assertEqual(['line1', 'line2', 'line3'], rv.events)

  def test_none_filtered(self):
    script = '''\
#!/usr/bin/env python
import sys
for line in ['keep1', 'skip_me', 'keep2', 'skip_too', 'keep3']:
  sys.stdout.write(line + '\\n')
  sys.stdout.flush()
'''
    tmp = self.make_temp_file(content=script, perm=0o0755, suffix='.py')
    def parser(stdout, stderr):
      line = (stdout or '').strip()
      if not line or 'skip' in line:
        return None
      return line
    rv = execute.execute_with_progress(tmp, line_parser=parser)
    self.assertEqual(['keep1', 'keep2', 'keep3'], rv.events)

  def test_progress_cb_called_live(self):
    script = '''\
#!/usr/bin/env python
import sys
for i in range(1, 4):
  sys.stdout.write(f'event{i}\\n')
  sys.stdout.flush()
'''
    tmp = self.make_temp_file(content=script, perm=0o0755, suffix='.py')
    cb_events = []
    def parser(stdout, stderr):
      line = (stdout or '').strip()
      return line if line else None
    def cb(event):
      cb_events.append(event)
    rv = execute.execute_with_progress(tmp, line_parser=parser, progress_cb=cb)
    self.assertEqual(rv.events, cb_events)

  def test_progress_cb_not_called_for_none(self):
    script = '''\
#!/usr/bin/env python
import sys
sys.stdout.write('ignored\\n')
sys.stdout.flush()
'''
    tmp = self.make_temp_file(content=script, perm=0o0755, suffix='.py')
    cb_called = []
    def parser(stdout, stderr):
      return None
    def cb(event):
      cb_called.append(event)
    rv = execute.execute_with_progress(tmp, line_parser=parser, progress_cb=cb)
    self.assertEqual([], rv.events)
    self.assertEqual([], cb_called)

  def test_result_has_execute_result(self):
    script = '''\
#!/usr/bin/env python
import sys
sys.stdout.write('hello\\n')
sys.stdout.flush()
'''
    tmp = self.make_temp_file(content=script, perm=0o0755, suffix='.py')
    def parser(stdout, stderr):
      return None
    rv = execute.execute_with_progress(tmp, line_parser=parser)
    self.assertEqual(0, rv.result.exit_code)
    self.assertIn('hello', rv.result.stdout)

  def test_stderr_lines_reach_parser(self):
    script = '''\
#!/usr/bin/env python
import sys
sys.stderr.write('err_line\\n')
sys.stderr.flush()
'''
    tmp = self.make_temp_file(content=script, perm=0o0755, suffix='.py')
    def parser(stdout, stderr):
      line = (stdout or '').strip()
      return line if line else None
    rv = execute.execute_with_progress(tmp, line_parser=parser, stderr_to_stdout=True)
    self.assertEqual(['err_line'], rv.events)

  def test_non_blocking_not_allowed_in_kwargs(self):
    def parser(stdout, stderr):
      return None
    with self.assertRaises(ValueError):
      execute.execute_with_progress('true', line_parser=parser, non_blocking=True)

  def test_parser_receives_correct_stdout_stderr(self):
    script = '''\
#!/usr/bin/env python
import sys
sys.stdout.write('from_stdout\\n')
sys.stdout.flush()
sys.stderr.write('from_stderr\\n')
sys.stderr.flush()
'''
    tmp = self.make_temp_file(content=script, perm=0o0755, suffix='.py')
    received = []
    def parser(stdout, stderr):
      if stdout and stdout.strip():
        received.append(('stdout', stdout.strip()))
      if stderr and stderr.strip():
        received.append(('stderr', stderr.strip()))
      return (stdout, stderr) if (stdout and stdout.strip()) or (stderr and stderr.strip()) else None
    rv = execute.execute_with_progress(tmp, line_parser=parser)
    stdout_events = [r for r in received if r[0] == 'stdout']
    stderr_events = [r for r in received if r[0] == 'stderr']
    self.assertTrue(any(v == 'from_stdout' for _, v in stdout_events))
    self.assertTrue(any(v == 'from_stderr' for _, v in stderr_events))

  def test_empty_output(self):
    script = '''\
#!/usr/bin/env python
import sys
sys.exit(0)
'''
    tmp = self.make_temp_file(content=script, perm=0o0755, suffix='.py')
    def parser(stdout, stderr):
      return None
    rv = execute.execute_with_progress(tmp, line_parser=parser)
    self.assertEqual([], rv.events)
    self.assertEqual(0, rv.result.exit_code)

  def test_high_line_count(self):
    script = '''\
#!/usr/bin/env python
import sys
for i in range(1000):
  sys.stdout.write(f'line{i}\\n')
  sys.stdout.flush()
'''
    tmp = self.make_temp_file(content=script, perm=0o0755, suffix='.py')
    def parser(stdout, stderr):
      line = (stdout or '').strip()
      return line if line else None
    rv = execute.execute_with_progress(tmp, line_parser=parser)
    self.assertEqual(1000, len(rv.events))
    self.assertEqual('line0', rv.events[0])
    self.assertEqual('line999', rv.events[999])

if __name__ == '__main__':
  import unittest
  unittest.main()
