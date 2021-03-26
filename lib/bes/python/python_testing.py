#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .python_exe import python_exe

from bes.system.log import logger

class python_testing(object):
  'Class to deal with the python testing.'

  _log = logger('python_exe')
  
  # The python 3.8 that comes with xcode is very non standard
  # crapping all kinds of droppings in non standard places such
  # as ~/Library/Caches even though the --no-cache-dir was given
  # so never use them for tests since they create side effects
  _EXCLUDE_SOURCES = ( 'xcode', )
  
  PYTHON_27 = python_exe.find_version('2.7', exclude_sources = _EXCLUDE_SOURCES)
  PYTHON_37 = python_exe.find_version('3.7', exclude_sources = _EXCLUDE_SOURCES)
  PYTHON_38 = python_exe.find_version('3.8', exclude_sources = _EXCLUDE_SOURCES)
  PYTHON_39 = python_exe.find_version('3.9', exclude_sources = _EXCLUDE_SOURCES)

  ALL_PYTHONS = [ p for p in [ _PYTHON_27, _PYTHON_37, _PYTHON_38, _PYTHON_39 ] if p ]
  ANY_PYTHON = next(iter([ p for p in _ALL_PYTHONS), None))
  ANY_PYTHON2 = next(iter([ p for p in _ALL_PYTHONS if python_exe.major_version(p) == 2]), None)
  ANY_PYTHON3 = next(iter([ p for p in _ALL_PYTHONS if python_exe.major_version(p) == 3]), None)

  _log.log_d('  PYTHON_27: {}'.format(PYTHON_27))
  _log.log_d('  PYTHON_37: {}'.format(PYTHON_37))
  _log.log_d('  PYTHON_38: {}'.format(PYTHON_38))
  _log.log_d('  PYTHON_39: {}'.format(PYTHON_39))
  _log.log_d('ALL_PYTHONS: {}'.format(' '.join(ALL_PYTHONS)))
  _log.log_d(' ANY_PYTHON: {}'.format(ANY_PYTHON))
  _log.log_d('ANY_PYTHON2: {}'.format(ANY_PYTHON2))
  _log.log_d('ANY_PYTHON3: {}'.format(ANY_PYTHON3))
