#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class list_util(object):
  'Misc utils to deal with lists.'
  
  @classmethod
  def reversed_enumerate(clazz, l):
    '''
    Generator that yields a list in reversed order
      from: https://stackoverflow.com/questions/529424/traverse-a-list-in-reverse-order-in-python
    '''
    for i in reversed(range(len(l))):
      yield i, l[i]
