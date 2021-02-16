
from .vmware_app_base import vmware_app_base

from bes.system.execute import execute

class vmware_app_windows(platform_determiner_base):

  #@abstractmethod
  def is_installed(self):
    'Return True if vmware is installed.'
    raise NotImplemented('is_installed')

  #@abstractmethod
  def is_running(self):
    'Return True if vmware is running.'
    raise NotImplemented('is_running')

  #@abstractmethod
  def ensure_running(self):
    'Ensure vmware is running.'
    raise NotImplemented('ensure_running')

  #@abstractmethod
  def ensure_stopped(self):
    'Ensure vmware is stopped.'
    raise NotImplemented('ensure_stopped')

  #@abstractmethod
  def host_type(self):
    'Host type form vmrun authentication.'
    return 'ws'

  #@abstractmethod
  def preferences_filename(self):
    'The full path to the preferneces filename.'
    return r'C:\Documents and Settings\All Users\Application Data\VMware\VMware Workstation\config.ini'
