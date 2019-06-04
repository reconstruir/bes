#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class read_only_dict(dict):
  'A read only dict - https://stackoverflow.com/questions/19022868/how-to-make-dictionary-read-only-in-python'

  def __readonly__(self, *args, **kwargs):
    raise RuntimeError('Cannot modify read_only_dict')
  __setitem__ = __readonly__
  __delitem__ = __readonly__
  pop = __readonly__
  popitem = __readonly__
  clear = __readonly__
  update = __readonly__
  setdefault = __readonly__
  del __readonly__
