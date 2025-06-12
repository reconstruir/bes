#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from ..system.check import check
from bes.common.string_util import string_util
from bes.system.host import host
from bes.system.log import log

from .bat_vmware_app import bat_vmware_app
from .vmware_error import vmware_error
from .vmware_properties_file import vmware_properties_file

class bat_vmware_inventory(vmware_properties_file):
  '''
  Class to deal with the vmware fusion/workstation vm inventory
  macos: ~/Library/Application Support/VMware Fusion/vmInventory
  linux: ?
  windows: ?
  '''
  def __init__(self, filename = None, backup = False):
    super(bat_vmware_inventory, self).__init__(filename, backup = backup)

  @classmethod
  def default_inventory_filename(clazz):
    return bat_vmware_app.inventory_filename()
    
  def remove_vm(self, vmx_filename):
    'Remove a vm from the inventory'
    check.check_string(vmx_filename)
    
    section = self._section_for_vm(vmx_filename)
    if not section:
      raise vmware_error('no vm found vmlists: "{}"'.format(vmx_filename))
    index = self._index_for_vm(vmx_filename)
    if index == None:
      raise vmware_error('no vm found in indeces: "{}"'.format(vmx_filename))
    self._remove_section(section, index)

  def remove_missing_vms(self):
    'Remove any vm that has a missing vmx file'
    missing_vms = self._missing_vms()
    for missing_vm in missing_vms:
      assert missing_vm
      self.remove_vm(missing_vm)

  def _missing_vms(self):
    result = []
    for vm in self.all_vms():
      if not path.exists(vm):
        result.append(vm)
    return result

  def all_vms(self):
    result = []
    d = self._to_dict()
    for section, values in d.items():
      if section.startswith('vmlist'):
        if 'config' in values:
          config = values['config']
          if config:
            result.append(config)
    return result
  
  def _remove_section(self, section, index):
    keys = [ key for key in self.keys() ]
    for key in keys:
      if key.startswith(section):
        if key.endswith('.config'):
          self.set_value(key, '')
        else:
          self.remove_value(key)
    
    indeces = self._indeces()
    assert index < len(indeces)
    indeces.pop(index)

    old_index_count = int(self.get_value('index.count'))
    assert old_index_count > 0
    new_index_count = old_index_count - 1
    
    for next_index, values in enumerate(indeces):
      for value_key, value in values.items():
        main_key = 'index{}.{}'.format(next_index, value_key)
        self.set_value(main_key, value)

    last_index_section = 'index{}'.format(old_index_count - 1)
    for key in keys:
      if key.startswith(last_index_section):
        self.remove_value(key)
        
    self.set_value('index.count', str(new_index_count))
    
  def _section_for_vm(self, vmx_filename):
    check.check_string(vmx_filename)
    
    d = self._to_dict()
    for section, values in d.items():
      if section.startswith('vmlist'):
        if 'config' in values:
          config = values['config']
          if config == vmx_filename:
            return section
    return None

  def _index_for_vm(self, vmx_filename):
    check.check_string(vmx_filename)
    
    d = self._to_dict()
    for section, values in d.items():
      if section.startswith('index'):
        if 'id' in values:
          index_id = values['id']
          if index_id == vmx_filename:
            return int(string_util.remove_head(section, 'index'))
    return None
  
  def _to_dict(self):
    result = {}
    for key, value in self.items():
      if key not in ( '.encoding', 'index.count' ):
        key_parts = key.split('.')
        section = key_parts[0]
        if not section in result:
          result[section] = {}
        value_key = '.'.join(key_parts[1:])
        assert value_key not in result[section]
        result[section][value_key] = value
    return result

  def _indeces(self):
    d = self._to_dict()
    index_dict = {}
    for key, values in d.items():
      if key.startswith('index'):
        index = int(string_util.remove_head(key, 'index'))
        index_dict[index] = values
    result = [ None ] * len(index_dict)
    for index, values in index_dict.items():
      result[index] = values
    assert None not in result
    return result
