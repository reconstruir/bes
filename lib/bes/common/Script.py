#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys

class Script(object):
  'Stuff for writing scripts'

  _spew = False

  @classmethod
  def name(clazz):
    'Return the name of the script.  A prettified argv[0].'
    return os.path.basename(sys.argv[0])

  @classmethod
  def make_blurb(clazz, message):
    'Make a blurb in the form - name: blurb.'
    return '%s: %s' % (Script.name(), message)

  @classmethod
  def blurb(clazz, message):
    'Print a blurb prefixed by the script name.'
    print('%s: %s' % (Script.name(), message))

  @classmethod
  def spew_blurb(clazz, message):
    'Print a blurb but only if the debug flag is set in the class.'
    if clazz._spew:
      clazz.blurb(message)

  @classmethod
  def blurb_and_raise(clazz, message):
    '''
    Print a blurb prefixed by the script name, and then raise a RuntimeError
    with the same blurb.
    '''
    msg = '%s: %s' % (Script.name(), message)
    print(msg)
    raise RuntimeError(msg)

  @classmethod
  def bail(clazz, message = None, exitCode = 1):
    'Print a blurb and exit with the given exitCode.'
    if message:
      Script.blurb(message)
    sys.exit(exitCode)

  @classmethod
  def usage(clazz, message, bail = False):
    'Print a usage blurb.'
    print('Usage: %s %s' % (Script.name(), message))
    if bail:
      sys.exit(1)

  @classmethod
  def set_spew(clazz, spew):
    'Set whether the script class is in spew mode causing extra spew.'
    clazz._spew = spew

  @classmethod
  def return_exit_code(clazz, boolean_status):
    'Return either 0 or 1 in the unix command sense according to the boolean_status.'
    if boolean_status:
      return 0
    return 1

  @classmethod
  def command_name_is_unique(clazz, names, name):
    'Return True if the given name prefix is unique.'
    count  = 0
    for next_name in names:
      if next_name.startswith(name):
        count += 1
    return count <= 1

  @classmethod
  def resolve_command_name(clazz, names, name):
    'Resolve the command name.  Deal with abbrebiations.'
    name = name.lower()
    names = [ n.lower() for n in names ]
    if not clazz.command_name_is_unique(names, name):
      return None
    for next_name in names:
      if next_name.lower().startswith(name.lower()):
        return next_name
    return None
