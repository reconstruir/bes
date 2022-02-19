#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

def global_func1(foo):
  pass

# comment2
class foo(object):
  'foo doc'
  
  def parse(self, arg):
    pass

# comment2
class bar(foo):
  'bar doc'

  def parse(self, arg):
    pass
  
