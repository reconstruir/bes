from something_base import something_base

class something(something_base):
  
  def __init__(self):
    self.__impl = _load(test_impl_import.something)
    
  def creator(self):
    return self.__impl.creator()
  
  def suck_level(self):
    return self.__impl.suck_level()
