#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys, types
from io import IOBase

class compat(object):
  'Hackery to help write code that works on both python 2 and 3.'
  
  if sys.version_info.major == 2:
    IS_PYTHON2 = True
    IS_PYTHON3 = False
  elif sys.version_info.major == 3:
    IS_PYTHON2 = False
    IS_PYTHON3 = True
  else:
    raise RuntimeError('unknown python version: %s' % (sys.version_info.major))

  # This bit here inspired by six
  # Copyright (c) 2010-2015 Benjamin Peterson
  #
  # Permission is hereby granted, free of charge, to any person obtaining a copy
  # of this software and associated documentation files (the "Software"), to deal
  # in the Software without restriction, including without limitation the rights
  # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  # copies of the Software, and to permit persons to whom the Software is
  # furnished to do so, subject to the following conditions:
  #
  # The above copyright notice and this permission notice shall be included in all
  # copies or substantial portions of the Software.
  #
  # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  # SOFTWARE.
  if IS_PYTHON3:
    STRING_TYPES = str,
    INTEGER_TYPES = int,
    CLASS_TYPES = type,
  else:
    STRING_TYPES = basestring,
    INTEGER_TYPES = (int, long)
    CLASS_TYPES = (type, types.ClassType)

  @classmethod
  def is_file(clazz, o):
    if clazz.IS_PYTHON3:
      return isinstance(o, IOBase)
    else:
      return isinstance(o, file)

  @classmethod
  def is_int(clazz, o):
    'Return True if o is an int.'
    return isinstance(o, clazz.INTEGER_TYPES)
    
  @classmethod
  def is_string(clazz, o):
    'Return True if o is an string.'
    return isinstance(o, clazz.STRING_TYPES)
    
  @classmethod
  def is_class(clazz, o):
    'Return True if o is a class.'
    return isinstance(o, clazz.CLASS_TYPES)
