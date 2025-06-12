#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.fs.file_util import file_util

from bes.vmware.bat_vmware_inventory import bat_vmware_inventory

class test_bat_vmware_inventory(unit_test):

  def test__to_dict(self):
    content = '''\
.encoding = "UTF-8"
vmlist1.CfgVersion = "8"
vmlist1.DisplayName = "|22win10_scratch|22"
vmlist1.IsCfgPathNormalized = "TRUE"
vmlist1.IsClone = "TRUE"
vmlist1.IsFavorite = "FALSE"
vmlist1.ItemID = "1"
vmlist1.ParentID = "0"
vmlist1.SeqID = "0"
vmlist1.State = "paused"
vmlist1.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 01"
vmlist1.config = "/Users/fred/vms/win10_scratch.vmwarevm/win10_scratch.vmx"
vmlist14.CfgVersion = "8"
vmlist14.DisplayName = "windows-10-pro"
vmlist14.IsCfgPathNormalized = "TRUE"
vmlist14.IsClone = "FALSE"
vmlist14.IsFavorite = "FALSE"
vmlist14.ItemID = "14"
vmlist14.ParentID = "0"
vmlist14.SeqID = "3"
vmlist14.State = "paused"
vmlist14.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 02"
vmlist14.config = "/Users/fred/vms/windows-10-pro.vmwarevm/windows-10-pro.vmx"
vmlist16.CfgVersion = "8"
vmlist16.DisplayName = "ubuntu-20.04"
vmlist16.IsCfgPathNormalized = "TRUE"
vmlist16.IsClone = "FALSE"
vmlist16.IsFavorite = "FALSE"
vmlist16.ItemID = "16"
vmlist16.ParentID = "0"
vmlist16.SeqID = "1"
vmlist16.State = "normal"
vmlist16.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 03"
vmlist16.config = "/Users/fred/vms/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx"
vmlist17.CfgVersion = "8"
vmlist17.DisplayName = "alpine-3.13.5"
vmlist17.IsCfgPathNormalized = "TRUE"
vmlist17.IsClone = "FALSE"
vmlist17.IsFavorite = "FALSE"
vmlist17.ItemID = "17"
vmlist17.ParentID = "0"
vmlist17.SeqID = "2"
vmlist17.State = "normal"
vmlist17.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 04"
vmlist17.config = "/Users/fred/vms/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx"
vmlist18.config = ""
vmlist19.config = ""
vmlist2.CfgVersion = "8"
vmlist2.DisplayName = "|22ubuntu-20.04_clone_20210426133244|22"
vmlist2.IsCfgPathNormalized = "TRUE"
vmlist2.IsClone = "TRUE"
vmlist2.IsFavorite = "FALSE"
vmlist2.ItemID = "2"
vmlist2.ParentID = "0"
vmlist2.SeqID = "4"
vmlist2.State = "broken"
vmlist2.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 05"
vmlist2.config = "/Users/fred/vms/ubuntu-20.04_clone_20210426133244.vmwarevm/ubuntu-20.04_clone_20210426133244.vmx"
vmlist3.config = ""
vmlist4.config = ""
vmlist5.config = ""
vmlist6.config = ""
vmlist7.config = ""
vmlist8.config = ""
vmlist9.config = ""
vmlist10.config = ""
vmlist11.config = ""
vmlist12.config = ""
vmlist13.config = ""
vmlist15.config = ""
index0.field0.name = "guest"
index0.field0.value = "other linux 5.x and later kernel 64-bit"
index0.field0.default = "TRUE"
index0.hostID = "localhost"
index0.id = "/Users/fred/vms/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx"
index0.field.count = "1"
index1.field0.name = "guest"
index1.field0.value = "ubuntu 64-bit"
index1.field0.default = "TRUE"
index1.hostID = "localhost"
index1.id = "/Users/fred/vms/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx"
index1.field.count = "1"
index2.field0.name = "guest"
index2.field0.value = "ubuntu 64-bit"
index2.field0.default = "TRUE"
index2.hostID = "localhost"
index2.id = "/Users/fred/vms/ubuntu-20.04_clone_20210426133244.vmwarevm/ubuntu-20.04_clone_20210426133244.vmx"
index2.field.count = "1"
index3.field0.name = "guest"
index3.field0.value = "windows 10 x64"
index3.field0.default = "TRUE"
index3.hostID = "localhost"
index3.id = "/Users/fred/vms/win10_scratch.vmwarevm/win10_scratch.vmx"
index3.field.count = "1"
index4.field0.name = "guest"
index4.field0.value = "windows 10 x64"
index4.field0.default = "TRUE"
index4.hostID = "localhost"
index4.id = "/Users/fred/vms/windows-10-pro.vmwarevm/windows-10-pro.vmx"
index4.field.count = "1"
index.count = "5"
'''
    i = bat_vmware_inventory(self.make_temp_file(content = content))
    self.assert_json_object_equal( {
      'index0': {'field.count': '1',
                 'field0.default': 'TRUE',
                 'field0.name': 'guest',
                 'field0.value': 'other linux 5.x and later kernel 64-bit',
                 'hostID': 'localhost',
                 'id': '/Users/fred/vms/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx'},
      'index1': {'field.count': '1',
                 'field0.default': 'TRUE',
                 'field0.name': 'guest',
                 'field0.value': 'ubuntu 64-bit',
                 'hostID': 'localhost',
                 'id': '/Users/fred/vms/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx'},
      'index2': {'field.count': '1',
                 'field0.default': 'TRUE',
                 'field0.name': 'guest',
                 'field0.value': 'ubuntu 64-bit',
                 'hostID': 'localhost',
                 'id': '/Users/fred/vms/ubuntu-20.04_clone_20210426133244.vmwarevm/ubuntu-20.04_clone_20210426133244.vmx'},
      'index3': {'field.count': '1',
                 'field0.default': 'TRUE',
                 'field0.name': 'guest',
                 'field0.value': 'windows 10 x64',
                 'hostID': 'localhost',
                 'id': '/Users/fred/vms/win10_scratch.vmwarevm/win10_scratch.vmx'},
      'index4': {'field.count': '1',
                 'field0.default': 'TRUE',
                 'field0.name': 'guest',
                 'field0.value': 'windows 10 x64',
                 'hostID': 'localhost',
                 'id': '/Users/fred/vms/windows-10-pro.vmwarevm/windows-10-pro.vmx'},
      'vmlist1': {'CfgVersion': '8',
                  'DisplayName': '|22win10_scratch|22',
                  'IsCfgPathNormalized': 'TRUE',
                  'IsClone': 'TRUE',
                  'IsFavorite': 'FALSE',
                  'ItemID': '1',
                  'ParentID': '0',
                  'SeqID': '0',
                  'State': 'paused',
                  'UUID': '00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 01',
                  'config': '/Users/fred/vms/win10_scratch.vmwarevm/win10_scratch.vmx'},
      'vmlist10': {'config': ''},
      'vmlist11': {'config': ''},
      'vmlist12': {'config': ''},
      'vmlist13': {'config': ''},
      'vmlist14': {'CfgVersion': '8',
                   'DisplayName': 'windows-10-pro',
                   'IsCfgPathNormalized': 'TRUE',
                   'IsClone': 'FALSE',
                   'IsFavorite': 'FALSE',
                   'ItemID': '14',
                   'ParentID': '0',
                   'SeqID': '3',
                   'State': 'paused',
                   'UUID': '00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 02',
                   'config': '/Users/fred/vms/windows-10-pro.vmwarevm/windows-10-pro.vmx'},
      'vmlist15': {'config': ''},
      'vmlist16': {'CfgVersion': '8',
                   'DisplayName': 'ubuntu-20.04',
                   'IsCfgPathNormalized': 'TRUE',
                   'IsClone': 'FALSE',
                   'IsFavorite': 'FALSE',
                   'ItemID': '16',
                   'ParentID': '0',
                   'SeqID': '1',
                   'State': 'normal',
                   'UUID': '00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 03',
                   'config': '/Users/fred/vms/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx'},
      'vmlist17': {'CfgVersion': '8',
                   'DisplayName': 'alpine-3.13.5',
                   'IsCfgPathNormalized': 'TRUE',
                   'IsClone': 'FALSE',
                   'IsFavorite': 'FALSE',
                   'ItemID': '17',
                   'ParentID': '0',
                   'SeqID': '2',
                   'State': 'normal',
                   'UUID': '00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 04',
                   'config': '/Users/fred/vms/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx'},
      'vmlist18': {'config': ''},
      'vmlist19': {'config': ''},
      'vmlist2': {'CfgVersion': '8',
                  'DisplayName': '|22ubuntu-20.04_clone_20210426133244|22',
                  'IsCfgPathNormalized': 'TRUE',
                  'IsClone': 'TRUE',
                  'IsFavorite': 'FALSE',
                  'ItemID': '2',
                  'ParentID': '0',
                  'SeqID': '4',
                  'State': 'broken',
                  'UUID': '00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 05',
                  'config': '/Users/fred/vms/ubuntu-20.04_clone_20210426133244.vmwarevm/ubuntu-20.04_clone_20210426133244.vmx'},
      'vmlist3': {'config': ''},
      'vmlist4': {'config': ''},
      'vmlist5': {'config': ''},
      'vmlist6': {'config': ''},
      'vmlist7': {'config': ''},
      'vmlist8': {'config': ''},
      'vmlist9': {'config': ''},
    }, i._to_dict() )

  def test_remove_vm(self):
    content = '''\
.encoding = "UTF-8"
vmlist1.CfgVersion = "8"
vmlist1.DisplayName = "|22win10_scratch|22"
vmlist1.IsCfgPathNormalized = "TRUE"
vmlist1.IsClone = "TRUE"
vmlist1.IsFavorite = "FALSE"
vmlist1.ItemID = "1"
vmlist1.ParentID = "0"
vmlist1.SeqID = "0"
vmlist1.State = "paused"
vmlist1.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 01"
vmlist1.config = "/Users/fred/vms/win10_scratch.vmwarevm/win10_scratch.vmx"
vmlist14.CfgVersion = "8"
vmlist14.DisplayName = "windows-10-pro"
vmlist14.IsCfgPathNormalized = "TRUE"
vmlist14.IsClone = "FALSE"
vmlist14.IsFavorite = "FALSE"
vmlist14.ItemID = "14"
vmlist14.ParentID = "0"
vmlist14.SeqID = "3"
vmlist14.State = "paused"
vmlist14.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 02"
vmlist14.config = "/Users/fred/vms/windows-10-pro.vmwarevm/windows-10-pro.vmx"
vmlist16.CfgVersion = "8"
vmlist16.DisplayName = "ubuntu-20.04"
vmlist16.IsCfgPathNormalized = "TRUE"
vmlist16.IsClone = "FALSE"
vmlist16.IsFavorite = "FALSE"
vmlist16.ItemID = "16"
vmlist16.ParentID = "0"
vmlist16.SeqID = "1"
vmlist16.State = "normal"
vmlist16.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 03"
vmlist16.config = "/Users/fred/vms/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx"
vmlist17.CfgVersion = "8"
vmlist17.DisplayName = "alpine-3.13.5"
vmlist17.IsCfgPathNormalized = "TRUE"
vmlist17.IsClone = "FALSE"
vmlist17.IsFavorite = "FALSE"
vmlist17.ItemID = "17"
vmlist17.ParentID = "0"
vmlist17.SeqID = "2"
vmlist17.State = "normal"
vmlist17.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 04"
vmlist17.config = "/Users/fred/vms/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx"
vmlist18.config = ""
vmlist19.config = ""
vmlist2.config = "/Users/fred/vms/ubuntu-20.04_clone_20210427134019.vmwarevm/ubuntu-20.04_clone_20210427134019.vmx"
vmlist2.DisplayName = "|22ubuntu-20.04_clone_20210427134019|22"
vmlist2.ParentID = "0"
vmlist2.ItemID = "2"
vmlist2.SeqID = "4"
vmlist2.IsFavorite = "FALSE"
vmlist2.IsClone = "TRUE"
vmlist2.CfgVersion = "8"
vmlist2.State = "broken"
vmlist2.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 05"
vmlist2.IsCfgPathNormalized = "TRUE"
vmlist3.config = ""
vmlist4.config = ""
vmlist5.config = ""
vmlist6.config = ""
vmlist7.config = ""
vmlist8.config = ""
vmlist9.config = ""
vmlist10.config = ""
vmlist11.config = ""
vmlist12.config = ""
vmlist13.config = ""
vmlist15.config = ""
index0.field0.name = "guest"
index0.field0.value = "other linux 5.x and later kernel 64-bit"
index0.field0.default = "TRUE"
index0.hostID = "localhost"
index0.id = "/Users/fred/vms/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx"
index0.field.count = "1"
index1.field0.name = "guest"
index1.field0.value = "ubuntu 64-bit"
index1.field0.default = "TRUE"
index1.hostID = "localhost"
index1.id = "/Users/fred/vms/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx"
index1.field.count = "1"
index2.field0.name = "guest"
index2.field0.value = "ubuntu 64-bit"
index2.field0.default = "TRUE"
index2.hostID = "localhost"
index2.id = "/Users/fred/vms/ubuntu-20.04_clone_20210427134019.vmwarevm/ubuntu-20.04_clone_20210427134019.vmx"
index2.field.count = "1"
index3.field0.name = "guest"
index3.field0.value = "windows 10 x64"
index3.field0.default = "TRUE"
index3.hostID = "localhost"
index3.id = "/Users/fred/vms/win10_scratch.vmwarevm/win10_scratch.vmx"
index3.field.count = "1"
index4.field0.name = "guest"
index4.field0.value = "windows 10 x64"
index4.field0.default = "TRUE"
index4.hostID = "localhost"
index4.id = "/Users/fred/vms/windows-10-pro.vmwarevm/windows-10-pro.vmx"
index4.field.count = "1"
index.count = "5"
'''

    expected_content = '''\
.encoding = "UTF-8"
index.count = "4"
index0.field.count = "1"
index0.field0.default = "TRUE"
index0.field0.name = "guest"
index0.field0.value = "other linux 5.x and later kernel 64-bit"
index0.hostID = "localhost"
index0.id = "/Users/fred/vms/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx"
index1.field.count = "1"
index1.field0.default = "TRUE"
index1.field0.name = "guest"
index1.field0.value = "ubuntu 64-bit"
index1.hostID = "localhost"
index1.id = "/Users/fred/vms/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx"
index2.field.count = "1"
index2.field0.default = "TRUE"
index2.field0.name = "guest"
index2.field0.value = "windows 10 x64"
index2.hostID = "localhost"
index2.id = "/Users/fred/vms/win10_scratch.vmwarevm/win10_scratch.vmx"
index3.field.count = "1"
index3.field0.default = "TRUE"
index3.field0.name = "guest"
index3.field0.value = "windows 10 x64"
index3.hostID = "localhost"
index3.id = "/Users/fred/vms/windows-10-pro.vmwarevm/windows-10-pro.vmx"
vmlist1.CfgVersion = "8"
vmlist1.DisplayName = "|22win10_scratch|22"
vmlist1.IsCfgPathNormalized = "TRUE"
vmlist1.IsClone = "TRUE"
vmlist1.IsFavorite = "FALSE"
vmlist1.ItemID = "1"
vmlist1.ParentID = "0"
vmlist1.SeqID = "0"
vmlist1.State = "paused"
vmlist1.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 01"
vmlist1.config = "/Users/fred/vms/win10_scratch.vmwarevm/win10_scratch.vmx"
vmlist10.config = ""
vmlist11.config = ""
vmlist12.config = ""
vmlist13.config = ""
vmlist14.CfgVersion = "8"
vmlist14.DisplayName = "windows-10-pro"
vmlist14.IsCfgPathNormalized = "TRUE"
vmlist14.IsClone = "FALSE"
vmlist14.IsFavorite = "FALSE"
vmlist14.ItemID = "14"
vmlist14.ParentID = "0"
vmlist14.SeqID = "3"
vmlist14.State = "paused"
vmlist14.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 02"
vmlist14.config = "/Users/fred/vms/windows-10-pro.vmwarevm/windows-10-pro.vmx"
vmlist15.config = ""
vmlist16.CfgVersion = "8"
vmlist16.DisplayName = "ubuntu-20.04"
vmlist16.IsCfgPathNormalized = "TRUE"
vmlist16.IsClone = "FALSE"
vmlist16.IsFavorite = "FALSE"
vmlist16.ItemID = "16"
vmlist16.ParentID = "0"
vmlist16.SeqID = "1"
vmlist16.State = "normal"
vmlist16.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 03"
vmlist16.config = "/Users/fred/vms/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx"
vmlist17.CfgVersion = "8"
vmlist17.DisplayName = "alpine-3.13.5"
vmlist17.IsCfgPathNormalized = "TRUE"
vmlist17.IsClone = "FALSE"
vmlist17.IsFavorite = "FALSE"
vmlist17.ItemID = "17"
vmlist17.ParentID = "0"
vmlist17.SeqID = "2"
vmlist17.State = "normal"
vmlist17.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 04"
vmlist17.config = "/Users/fred/vms/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx"
vmlist18.config = ""
vmlist19.config = ""
vmlist2.config = ""
vmlist3.config = ""
vmlist4.config = ""
vmlist5.config = ""
vmlist6.config = ""
vmlist7.config = ""
vmlist8.config = ""
vmlist9.config = ""
'''
    i = bat_vmware_inventory(self.make_temp_file(content = content))
    i.remove_vm('/Users/fred/vms/ubuntu-20.04_clone_20210427134019.vmwarevm/ubuntu-20.04_clone_20210427134019.vmx')
    self.assert_text_file_equal( expected_content, i.filename, strip = True, native_line_breaks = True)

  @unit_test_function_skip.skip_if_not_unix()
  def test_remove_missing_vms_none_missing(self):
    tmp_vm_dir = self.make_temp_dir(suffix = '.vms')
    tmp_vmx_content = '''
.encoding = "UTF-8"
    '''
    content = '''\
.encoding = "UTF-8"
vmlist1.CfgVersion = "8"
vmlist1.DisplayName = "|22win10_scratch|22"
vmlist1.IsCfgPathNormalized = "TRUE"
vmlist1.IsClone = "TRUE"
vmlist1.IsFavorite = "FALSE"
vmlist1.ItemID = "1"
vmlist1.ParentID = "0"
vmlist1.SeqID = "0"
vmlist1.State = "paused"
vmlist1.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 01"
vmlist1.config = "{tmp_vm_dir}/win10_scratch.vmwarevm/win10_scratch.vmx"
vmlist14.CfgVersion = "8"
vmlist14.DisplayName = "windows-10-pro"
vmlist14.IsCfgPathNormalized = "TRUE"
vmlist14.IsClone = "FALSE"
vmlist14.IsFavorite = "FALSE"
vmlist14.ItemID = "14"
vmlist14.ParentID = "0"
vmlist14.SeqID = "3"
vmlist14.State = "paused"
vmlist14.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 02"
vmlist14.config = "{tmp_vm_dir}/windows-10-pro.vmwarevm/windows-10-pro.vmx"
vmlist16.CfgVersion = "8"
vmlist16.DisplayName = "ubuntu-20.04"
vmlist16.IsCfgPathNormalized = "TRUE"
vmlist16.IsClone = "FALSE"
vmlist16.IsFavorite = "FALSE"
vmlist16.ItemID = "16"
vmlist16.ParentID = "0"
vmlist16.SeqID = "1"
vmlist16.State = "normal"
vmlist16.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 03"
vmlist16.config = "{tmp_vm_dir}/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx"
vmlist17.CfgVersion = "8"
vmlist17.DisplayName = "alpine-3.13.5"
vmlist17.IsCfgPathNormalized = "TRUE"
vmlist17.IsClone = "FALSE"
vmlist17.IsFavorite = "FALSE"
vmlist17.ItemID = "17"
vmlist17.ParentID = "0"
vmlist17.SeqID = "2"
vmlist17.State = "normal"
vmlist17.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 04"
vmlist17.config = "{tmp_vm_dir}/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx"
vmlist18.config = ""
vmlist19.config = ""
vmlist2.config = "{tmp_vm_dir}/ubuntu-20.04_clone_20210427134019.vmwarevm/ubuntu-20.04_clone_20210427134019.vmx"
vmlist2.DisplayName = "|22ubuntu-20.04_clone_20210427134019|22"
vmlist2.ParentID = "0"
vmlist2.ItemID = "2"
vmlist2.SeqID = "4"
vmlist2.IsFavorite = "FALSE"
vmlist2.IsClone = "TRUE"
vmlist2.CfgVersion = "8"
vmlist2.State = "broken"
vmlist2.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 05"
vmlist2.IsCfgPathNormalized = "TRUE"
vmlist3.config = ""
vmlist4.config = ""
vmlist5.config = ""
vmlist6.config = ""
vmlist7.config = ""
vmlist8.config = ""
vmlist9.config = ""
vmlist10.config = ""
vmlist11.config = ""
vmlist12.config = ""
vmlist13.config = ""
vmlist15.config = ""
index0.field0.name = "guest"
index0.field0.value = "other linux 5.x and later kernel 64-bit"
index0.field0.default = "TRUE"
index0.hostID = "localhost"
index0.id = "{tmp_vm_dir}/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx"
index0.field.count = "1"
index1.field0.name = "guest"
index1.field0.value = "ubuntu 64-bit"
index1.field0.default = "TRUE"
index1.hostID = "localhost"
index1.id = "{tmp_vm_dir}/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx"
index1.field.count = "1"
index2.field0.name = "guest"
index2.field0.value = "ubuntu 64-bit"
index2.field0.default = "TRUE"
index2.hostID = "localhost"
index2.id = "{tmp_vm_dir}/ubuntu-20.04_clone_20210427134019.vmwarevm/ubuntu-20.04_clone_20210427134019.vmx"
index2.field.count = "1"
index3.field0.name = "guest"
index3.field0.value = "windows 10 x64"
index3.field0.default = "TRUE"
index3.hostID = "localhost"
index3.id = "{tmp_vm_dir}/win10_scratch.vmwarevm/win10_scratch.vmx"
index3.field.count = "1"
index4.field0.name = "guest"
index4.field0.value = "windows 10 x64"
index4.field0.default = "TRUE"
index4.hostID = "localhost"
index4.id = "{tmp_vm_dir}/windows-10-pro.vmwarevm/windows-10-pro.vmx"
index4.field.count = "1"
index.count = "5"
'''.format(tmp_vm_dir = tmp_vm_dir)

    expected_content = '''\
.encoding = "UTF-8"
index.count = "4"
index0.field.count = "1"
index0.field0.default = "TRUE"
index0.field0.name = "guest"
index0.field0.value = "other linux 5.x and later kernel 64-bit"
index0.hostID = "localhost"
index0.id = "{tmp_vm_dir}/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx"
index1.field.count = "1"
index1.field0.default = "TRUE"
index1.field0.name = "guest"
index1.field0.value = "ubuntu 64-bit"
index1.hostID = "localhost"
index1.id = "{tmp_vm_dir}/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx"
index2.field.count = "1"
index2.field0.default = "TRUE"
index2.field0.name = "guest"
index2.field0.value = "windows 10 x64"
index2.hostID = "localhost"
index2.id = "{tmp_vm_dir}/win10_scratch.vmwarevm/win10_scratch.vmx"
index3.field.count = "1"
index3.field0.default = "TRUE"
index3.field0.name = "guest"
index3.field0.value = "windows 10 x64"
index3.hostID = "localhost"
index3.id = "{tmp_vm_dir}/windows-10-pro.vmwarevm/windows-10-pro.vmx"
vmlist1.CfgVersion = "8"
vmlist1.DisplayName = "|22win10_scratch|22"
vmlist1.IsCfgPathNormalized = "TRUE"
vmlist1.IsClone = "TRUE"
vmlist1.IsFavorite = "FALSE"
vmlist1.ItemID = "1"
vmlist1.ParentID = "0"
vmlist1.SeqID = "0"
vmlist1.State = "paused"
vmlist1.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 01"
vmlist1.config = "{tmp_vm_dir}/win10_scratch.vmwarevm/win10_scratch.vmx"
vmlist10.config = ""
vmlist11.config = ""
vmlist12.config = ""
vmlist13.config = ""
vmlist14.CfgVersion = "8"
vmlist14.DisplayName = "windows-10-pro"
vmlist14.IsCfgPathNormalized = "TRUE"
vmlist14.IsClone = "FALSE"
vmlist14.IsFavorite = "FALSE"
vmlist14.ItemID = "14"
vmlist14.ParentID = "0"
vmlist14.SeqID = "3"
vmlist14.State = "paused"
vmlist14.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 02"
vmlist14.config = "{tmp_vm_dir}/windows-10-pro.vmwarevm/windows-10-pro.vmx"
vmlist15.config = ""
vmlist16.CfgVersion = "8"
vmlist16.DisplayName = "ubuntu-20.04"
vmlist16.IsCfgPathNormalized = "TRUE"
vmlist16.IsClone = "FALSE"
vmlist16.IsFavorite = "FALSE"
vmlist16.ItemID = "16"
vmlist16.ParentID = "0"
vmlist16.SeqID = "1"
vmlist16.State = "normal"
vmlist16.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 03"
vmlist16.config = "{tmp_vm_dir}/ubuntu-20.04.vmwarevm/ubuntu-20.04.vmx"
vmlist17.CfgVersion = "8"
vmlist17.DisplayName = "alpine-3.13.5"
vmlist17.IsCfgPathNormalized = "TRUE"
vmlist17.IsClone = "FALSE"
vmlist17.IsFavorite = "FALSE"
vmlist17.ItemID = "17"
vmlist17.ParentID = "0"
vmlist17.SeqID = "2"
vmlist17.State = "normal"
vmlist17.UUID = "00 11 22 33 44 55 66 77-88 99 aa bb cc dd 00 04"
vmlist17.config = "{tmp_vm_dir}/alpine-3.13.5.vmwarevm/alpine-3.13.5.vmx"
vmlist18.config = ""
vmlist19.config = ""
vmlist2.config = ""
vmlist3.config = ""
vmlist4.config = ""
vmlist5.config = ""
vmlist6.config = ""
vmlist7.config = ""
vmlist8.config = ""
vmlist9.config = ""
'''.format(tmp_vm_dir = tmp_vm_dir)
    i = bat_vmware_inventory(self.make_temp_file(content = content))
    for next_vm in i.all_vms():
      if not next_vm.endswith('ubuntu-20.04_clone_20210427134019.vmx'):
        file_util.save(next_vm, tmp_vmx_content)
    i.remove_missing_vms()
    self.assert_text_file_equal( expected_content, i.filename, strip = True, native_line_breaks = True)
    
if __name__ == '__main__':
  unit_test.main()
