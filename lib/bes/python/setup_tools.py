#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs.dir_util import dir_util
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util

class setup_tools(object):
  'Class to deal with setup_tools things.'

  @classmethod
  def read_easy_install_pth(clazz, filename):
    content = file_util.read(filename).strip()
    lines = content.decode('utf-8').split('\n')
    if len(lines) < 2:
      raise RuntimeError('Invalid easy-install.pth(1): %s' % (filename))
    if not lines[0].startswith('import sys'):
      raise RuntimeError('Invalid easy-install.pth(2): %s' % (filename))
    if not lines[-1].startswith('import sys'):
      raise RuntimeError('Invalid easy-install.pth(3): %s' % (filename))
    eggs = lines[1:-1]
    return [ path.normpath(egg) for egg in eggs ]
    
  @classmethod
  def list_eggs(clazz, d):
    return dir_util.list(d, patterns = [ '*.egg', '*.egg-info' ], relative = True, basename = True)

  @classmethod
  def update_egg_directory(clazz, d):
    if not path.exists(d):
      return
    if not path.isdir(d):
      raise RuntimeError('Not a directory: %s' % (d))
    eggs = clazz.list_eggs(d)
    eggs = [ './%s' % (egg) for egg in eggs ]

    eggs_content = '\n'.join(eggs)
    easy_install_dot_pth = path.join(d, clazz.EASY_INSTALL_DOT_PTH_FILENAME)
    easy_install_dot_pth_content = clazz.EASY_INSTALL_DOT_PTH_TEMPLATE % (eggs_content)
    file_util.save(easy_install_dot_pth, content = easy_install_dot_pth_content, mode = 0o644)
    clazz.update_site_dot_py(d)
    
  @classmethod
  def update_site_dot_py(clazz, d):
    if not path.exists(d):
      return
    if not path.isdir(d):
      raise RuntimeError('Not a directory: %s' % (d))
    site_py_path = path.join(d, clazz.SITE_DOT_PY_FILENAME)
    old_content = None
    if path.exists(site_py_path):
      if not path.isfile(site_py_path):
        raise RuntimeError('Not a regular file: %s' % (site_py_path))
      old_content = file_util.read(site_py_path)
    if old_content == clazz.SITE_DOT_PY_CONTENT:
      return
    file_util.save(site_py_path, content = clazz.SITE_DOT_PY_CONTENT, mode = 0o644)
    
  EASY_INSTALL_DOT_PTH_FILENAME = 'easy-install.pth'
  SITE_DOT_PY_FILENAME = 'site.py'

  EASY_INSTALL_DOT_PTH_TEMPLATE = '''\
import sys; sys.__plen = len(sys.path)
%s
import sys; new = sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p = getattr(sys, '__egginsert', 0); sys.path[p:p] = new; sys.__egginsert = p + len(new)
'''

  # From setuptools 19.4
  SITE_DOT_PY_CONTENT = '''\
def __boot():
    import sys
    import os
    PYTHONPATH = os.environ.get('PYTHONPATH')
    if PYTHONPATH is None or (sys.platform=='win32' and not PYTHONPATH):
        PYTHONPATH = []
    else:
        PYTHONPATH = PYTHONPATH.split(os.pathsep)

    pic = getattr(sys,'path_importer_cache',{})
    stdpath = sys.path[len(PYTHONPATH):]
    mydir = os.path.dirname(__file__)
    #print "searching",stdpath,sys.path

    for item in stdpath:
        if item==mydir or not item:
            continue    # skip if current dir. on Windows, or my own directory
        importer = pic.get(item)
        if importer is not None:
            loader = importer.find_module('site')
            if loader is not None:
                # This should actually reload the current module
                loader.load_module('site')
                break
        else:
            try:
                import imp # Avoid import loop in Python >= 3.3
                stream, path, descr = imp.find_module('site',[item])
            except ImportError:
                continue
            if stream is None:
                continue
            try:
                # This should actually reload the current module
                imp.load_module('site',stream,path,descr)
            finally:
                stream.close()
            break
    else:
        raise ImportError("Couldn't find the real 'site' module")

    #print "loaded", __file__

    known_paths = dict([(makepath(item)[1],1) for item in sys.path]) # 2.2 comp

    oldpos = getattr(sys,'__egginsert',0)   # save old insertion position
    sys.__egginsert = 0                     # and reset the current one

    for item in PYTHONPATH:
        addsitedir(item)

    sys.__egginsert += oldpos           # restore effective old position

    d, nd = makepath(stdpath[0])
    insert_at = None
    new_path = []

    for item in sys.path:
        p, np = makepath(item)

        if np==nd and insert_at is None:
            # We've hit the first 'system' path entry, so added entries go here
            insert_at = len(new_path)

        if np in known_paths or insert_at is None:
            new_path.append(item)
        else:
            # new path after the insert point, back-insert it
            new_path.insert(insert_at, item)
            insert_at += 1

    sys.path[:] = new_path

if __name__=='site':
    __boot()
    del __boot
    
'''
