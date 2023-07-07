#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_util import file_util
from bes.pyinstaller.pyinstaller import pyinstaller
from bes.ssh_config.ssh_key_scan import ssh_key_scan
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip

class test_ssh_key_scan(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_unix()
    pyinstaller.raise_skip_if_is_binary()

  def test_scan(self):
    s = ssh_key_scan.scan('bitbucket.org')
    self.assertEqual( 2, len(s.hostnames) )
    self.assertEqual( 'bitbucket.org', s.hostnames[0] )
    self.assertEqual( 'ssh-rsa', s.key_type )
    self.assertEqual( 'AAAAB3NzaC1yc2EAAAADAQABAAABgQDQeJzhupRu0u0cdegZIa8e86EG2qOCsIsD1Xw0xSeiPDlCr7kq97NLmMbpKTX6Esc30NuoqEEHCuc7yWtwp8dI76EEEB1VqY9QJq6vk+aySyboD5QF61I/1WeTwu+deCbgKMGbUijeXhtfbxSxm6JwGrXrhBdofTsbKRUsrN1WoNgUa8uqN1Vx6WAJw1JHPhglEGGHea6QICwJOAr/6mrui/oB7pkaWKHj3z7d1IC4KWLtY47elvjbaTlkN04Kc/5LFEirorGYVbt15kAUlqGM65pk6ZBxtaO3+30LVlORZkxOh+LKL/BvbZ/iRNhItLqNyieoQj/uh/7Iv4uyH/cV/0b4WDSd3DptigWq84lJubb9t/DnZlrJazxyDCulTmKdOR7vs9gMTo+uoIrPSb8ScTtvw65+odKAlBj59dhnVp9zd7QUojOpXlL62Aw56U4oO+FALuevvMjiWeavKhJqlR7i5n9srYcrNV7ttmDw7kf/97P5zauIhxcjX+xHv4M=', s.key )
    self.assertTrue( s.comment.startswith('# bitbucket.org:22 SSH-2.0') )
    
if __name__ == '__main__':
  unit_test.main()
