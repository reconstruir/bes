#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.system.host import host
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.testing.program_unit_test import program_unit_test

class test_vm_builder_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '..', '..', '..', '..', 'bin', 'best.py')
  
  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_vm_builder_ssh_setup(self):

    git_access_ssh_public_key_content = r'''
ssh-rsa test_public_bitbucket_key fred@bedrock
'''
    git_access_ssh_private_key_content = r'''
-----BEGIN RSA PRIVATE KEY-----
test_private_bitbucket_key
-----END RSA PRIVATE KEY-----
'''
    git_access_ssh_public_key = self.make_temp_file(content = git_access_ssh_public_key_content)
    git_access_ssh_private_key = self.make_temp_file(content = git_access_ssh_private_key_content)
    
    vm_builder_access_ssh_public_key_content = r'''
ssh-rsa test_public_access_key sally@bedrock
'''
    vm_builder_access_ssh_private_key_content = r'''
-----BEGIN RSA PRIVATE KEY-----
test_private_access_key
-----END RSA PRIVATE KEY-----
'''
    vm_builder_access_ssh_public_key = self.make_temp_file(content = vm_builder_access_ssh_public_key_content)

    tmp_dir = self.make_temp_dir(suffix = '.ssh')
    
    args = [
      'vm_builder',
      'vm_builder_ssh_setup',
      '--dont-include-ip-address',
      '--dont-include-comment',
      tmp_dir,
      'fred',
      git_access_ssh_public_key,
      git_access_ssh_private_key,
      'bitbucket.org',
      vm_builder_access_ssh_public_key,
    ]
    
    rv = self.run_program(self._program, args)
    self.assertEqual( 0, rv.exit_code )
    files = file_find.find(tmp_dir)
    self.assertEqual( [
      'authorized_keys',
      'config',
      'id_rsa_bitbucket_org',
      'id_rsa_bitbucket_org.pub',
      'known_hosts',
      'vm_builder_access_key.pub',
    ], files )

    private_key = path.join(tmp_dir, 'id_rsa_bitbucket_org')
    config_text = file_util.read(path.join(tmp_dir, 'config'), codec = 'utf-8').strip()
    expected_config = '''
Host bitbucket.org
  Hostname bitbucket.org
  IdentityFile {private_key}
  User fred
'''.format(private_key = private_key)
    self.assert_string_equal( expected_config, config_text, strip = True, multi_line = True, native_line_breaks = True )

    known_hosts_text = file_util.read(path.join(tmp_dir, 'known_hosts'), codec = 'utf-8').strip()
    expected_known_hosts = '''
bitbucket.org ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDQeJzhupRu0u0cdegZIa8e86EG2qOCsIsD1Xw0xSeiPDlCr7kq97NLmMbpKTX6Esc30NuoqEEHCuc7yWtwp8dI76EEEB1VqY9QJq6vk+aySyboD5QF61I/1WeTwu+deCbgKMGbUijeXhtfbxSxm6JwGrXrhBdofTsbKRUsrN1WoNgUa8uqN1Vx6WAJw1JHPhglEGGHea6QICwJOAr/6mrui/oB7pkaWKHj3z7d1IC4KWLtY47elvjbaTlkN04Kc/5LFEirorGYVbt15kAUlqGM65pk6ZBxtaO3+30LVlORZkxOh+LKL/BvbZ/iRNhItLqNyieoQj/uh/7Iv4uyH/cV/0b4WDSd3DptigWq84lJubb9t/DnZlrJazxyDCulTmKdOR7vs9gMTo+uoIrPSb8ScTtvw65+odKAlBj59dhnVp9zd7QUojOpXlL62Aw56U4oO+FALuevvMjiWeavKhJqlR7i5n9srYcrNV7ttmDw7kf/97P5zauIhxcjX+xHv4M=
'''
    self.assert_string_equal( expected_known_hosts, known_hosts_text, strip = True, multi_line = True, native_line_breaks = True )

    abs_files = [ path.join(tmp_dir, f) for f in files ]
    if host.is_unix():
      for filename in abs_files:
        self.assertEqual( 0o0600, file_util.mode(filename) )

  def test_vm_host_ssh_setup(self):
    vm_builder_access_ssh_public_key_content = r'''
ssh-rsa test_public_access_key sally@bedrock
'''
    vm_builder_access_ssh_private_key_content = r'''
-----BEGIN RSA PRIVATE KEY-----
test_private_access_key
-----END RSA PRIVATE KEY-----
'''
    vm_builder_access_ssh_public_key = self.make_temp_file(content = vm_builder_access_ssh_public_key_content)
    vm_builder_access_ssh_private_key = self.make_temp_file(content = vm_builder_access_ssh_private_key_content)
    tmp_dir = self.make_temp_dir(suffix = '.ssh')
    
    args = [
      'vm_builder',
      'vm_host_ssh_setup',
      '--dont-include-ip-address',
      '--dont-include-comment',
      tmp_dir,
      'vm_host_access_key',
      'fred',
      vm_builder_access_ssh_public_key,
      vm_builder_access_ssh_private_key,
    ]
    
    rv = self.run_program(self._program, args)
    self.assertEqual( 0, rv.exit_code )
    files = file_find.find(tmp_dir)
    print(files)
    self.assertEqual( [
      'vm_host_access_key',
      'vm_host_access_key.pub',
    ], files )
    return
      
    private_key = path.join(tmp_dir, 'id_rsa_bitbucket_org')
    expected_config = '''
Host bitbucket.org
  Hostname bitbucket.org
  IdentityFile {private_key}
  User fred
'''.format(private_key = private_key)
    self.assert_text_file_equal( expected_config, path.join(tmp_dir, 'config'), codec = 'utf-8', strip = True, native_line_breaks = True )

    expected_known_hosts = '''
bitbucket.org ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDQeJzhupRu0u0cdegZIa8e86EG2qOCsIsD1Xw0xSeiPDlCr7kq97NLmMbpKTX6Esc30NuoqEEHCuc7yWtwp8dI76EEEB1VqY9QJq6vk+aySyboD5QF61I/1WeTwu+deCbgKMGbUijeXhtfbxSxm6JwGrXrhBdofTsbKRUsrN1WoNgUa8uqN1Vx6WAJw1JHPhglEGGHea6QICwJOAr/6mrui/oB7pkaWKHj3z7d1IC4KWLtY47elvjbaTlkN04Kc/5LFEirorGYVbt15kAUlqGM65pk6ZBxtaO3+30LVlORZkxOh+LKL/BvbZ/iRNhItLqNyieoQj/uh/7Iv4uyH/cV/0b4WDSd3DptigWq84lJubb9t/DnZlrJazxyDCulTmKdOR7vs9gMTo+uoIrPSb8ScTtvw65+odKAlBj59dhnVp9zd7QUojOpXlL62Aw56U4oO+FALuevvMjiWeavKhJqlR7i5n9srYcrNV7ttmDw7kf/97P5zauIhxcjX+xHv4M=
'''
    self.assert_text_file_equal( expected_known_hosts, path.join(tmp_dir, 'known_hosts'), codec = 'utf-8', strip = True, native_line_breaks = True )

    abs_files = [ path.join(tmp_dir, f) for f in files ]
    if host.is_unix():
      for filename in abs_files:
        self.assertEqual( 0o0600, file_util.mode(filename) )
      
if __name__ == '__main__':
  program_unit_test.main()
