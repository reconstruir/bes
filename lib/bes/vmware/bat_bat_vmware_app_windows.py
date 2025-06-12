
from .bat_bat_vmware_app_base import bat_bat_vmware_app_base

from bes.system.execute import execute

class bat_bat_vmware_app_windows(bat_bat_vmware_app_base):

  @classmethod
  #@abstractmethod
  def is_installed(clazz):
    'Return True if vmware is installed.'
    raise NotImplemented('is_installed')

  @classmethod
  #@abstractmethod
  def is_running(clazz):
    'Return True if vmware is running.'
    raise NotImplemented('is_running')

  @classmethod
  #@abstractmethod
  def ensure_running(clazz):
    'Ensure vmware is running.'
    raise NotImplemented('ensure_running')

  @classmethod
  #@abstractmethod
  def ensure_stopped(clazz):
    'Ensure vmware is stopped.'
    raise NotImplemented('ensure_stopped')

  @classmethod
  #@abstractmethod
  def host_type(clazz):
    'Host type form vmrun authentication.'
    return 'ws'

  @classmethod
  #@abstractmethod
  def preferences_filename(clazz):
    'The full path to the preferences filename.'
    return r'C:\Documents and Settings\All Users\Application Data\VMware\VMware Workstation\config.ini'

  @classmethod
  #@abstractmethod
  def inventory_filename(self):
    'The full path to the inventory filename.'
    raise NotImplemented('inventory_filename')
  
  @classmethod
  #@abstractmethod
  def vmrun_exe_path(clazz):
    'The full path to the vmrun executable.'
    raise NotImplemented('vmrun_exe_path')
