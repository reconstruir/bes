
from bes.vmware.vmware_properties_file import vmware_properties_file

p = vmware_properties_file('save1/vmInventory')
for key in p.keys():
  print(key)
  
