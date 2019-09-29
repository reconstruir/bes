#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect

# inspect.currentframe().f_back.f_locals

def dump(o, name = None):
#  _, filename, line_number, _, _, _ = inspect.stack()[1]
#  loc = inspect.currentframe().f_back.f_locals
#  print('loc: %s' % (loc))
#  print('nam: %s' % (o.__name__))
#  name = 'dunno'
  if name:
    print('DUMP: %s: %s - %s' % (name, o, type(o)))
  else:
    print('DUMP: %s - %s' % (o, type(o)))
    #
#    raise TypeError('\"%s\" should be of type \"%s\" instead of \"%s\" at %s line %d' % (name,
#                                                                                         type_blurb,
#                                                                                         type(o).__name__,
  
