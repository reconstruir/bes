#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import copy, os, os.path as path

from bes.compat.plistlib import plistlib_loads

from bes.fs.file_check import file_check
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.file_copy import file_copy
from bes.fs.temp_file import temp_file

from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import log

#log.configure('dmg=info format=brief')

class dmg(object):
  'Class to deal with dmg files on macos.'

  mount_info = namedtuple('mount_info', 'filename, mount_point, entries')

  _DEBUG = False
  
  @classmethod
  def is_dmg_file(clazz, filename):
    '''
    Return True if file is a valid DMG file by checking the magic at the begging of the trailing 512 bytes
    From http://newosxbook.com/DMG.html
    '''
    with open(filename, 'rb') as fin:
      try:
        fin.seek(-512, os.SEEK_END)
        trailer = fin.read(512)
        return trailer[0:4].decode('ascii') == 'koly'
      except IOError:
        return False
      except UnicodeDecodeError as ex:
        return False

  @classmethod
  def info(clazz):
    rv = clazz._execute_cmd('hdiutil', 'info', '-plist')
    return plistlib_loads(rv.stdout.encode('utf-8')).get('images', [])

  @classmethod
  def is_mounted(clazz, filename):
    pass
  
  @classmethod
  def contents(clazz, dmg):
    file_check.check_file(dmg)
    mnt = clazz._mount_at_temp_dir(dmg)
    files = file_find.find(mnt.mount_point, relative = True, file_type = file_find.FILE_OR_LINK)
    clazz._eject(mnt.mount_point)
    return files

  @classmethod
  def extract(clazz, dmg, dst_dir):
    file_check.check_file(dmg)
    file_util.mkdir(dst_dir)
    mnt = clazz._mount_at_temp_dir(dmg)
    #clazz._fix_extracted_dir_permissions(mnt.mount_point)
    file_copy.copy_tree(mnt.mount_point, dst_dir)
    clazz._eject(mnt.mount_point)

  @classmethod
  def _fix_extracted_dir_permissions(clazz, d):
    'Sometimes when a dmg is extracted, there will be directories with messed up permissions.'
    dirs = file_find.find(d, relative = False, file_type = file_find.DIR)
    for d in dirs:
      os.chmod(d, 0o755)

  @classmethod
  def _mount_at_temp_dir(clazz, dmg):
    file_check.check_file(dmg)
    tmp_dir = temp_file.make_temp_dir()
    rv = clazz._execute_cmd('hdiutil', 'attach', '-mountpoint', tmp_dir, '-plist', '-readonly', dmg)
    entries = plistlib_loads(rv.stdout.encode('utf-8'))
    return clazz.mount_info(dmg, tmp_dir, entries.get('system-entities', []))

  @classmethod
  def _eject(clazz, mount_point):
    clazz._execute_cmd('hdiutil', 'eject', mount_point)
  
  @classmethod
  def _execute_cmd(clazz, *args):
    args = copy.deepcopy(list(args))
#    if clazz._DEBUG:
#      args.append('-debug')
    cmd = ' '.join(args)
    clazz.log_i('executing: "%s"' % (cmd))
    if clazz._DEBUG:
      print('DMG: executing: %s' % (cmd))
    return execute.execute(cmd)

  @classmethod
  def set_debug(clazz, debug):
    clazz._DEBUG = debug
  
log.add_logging(dmg, 'dmg')
