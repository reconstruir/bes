#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.pip.pip_exe import pip_exe

class test_pip_exe(unit_test):

  def test_version_info(self):
    content = '''\
#!/bin/bash
echo "pip 666.0.1 from /foo/site-packages/pip (python 2.7)"
exit 0
'''
    fake_exe = self.make_temp_file(content = content, perm = 0o0755)
    self.assertEqual( ( '666.0.1', '/foo/site-packages/pip', '2.7' ), pip_exe.version_info(fake_exe) )

  def test_version(self):
    content = '''\
#!/bin/bash
echo "pip 666.0.1 from /foo/site-packages/pip (python 2.7)"
exit 0
'''
    fake_exe = self.make_temp_file(content = content, perm = 0o0755)
    self.assertEqual( '666.0.1', pip_exe.version(fake_exe) )

if __name__ == '__main__':
  unit_test.main()
