#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import types

class bcallable(object):

  @classmethod
  def name(clazz, callable_obj):
    if isinstance(callable_obj, types.MethodType):
      # Bound method: method name, class name, and module name
      method_name = callable_obj.__name__
      class_name = callable_obj.__self__.__class__.__name__
      module_name = callable_obj.__self__.__class__.__module__
      return f"{module_name}.{class_name}.{method_name}"
  
    elif isinstance(callable_obj, types.FunctionType):
      # Unbound function or method
      function_name = callable_obj.__name__
      module_name = callable_obj.__module__
      return f"{module_name}.{function_name}"
  
    elif isinstance(callable_obj, types.BuiltinFunctionType):
      # Built-in function or method
      return callable_obj.__name__
  
    elif hasattr(callable_obj, '__call__'):
      # Callable object (e.g., a class with __call__ defined)
      class_name = callable_obj.__class__.__name__
      module_name = callable_obj.__class__.__module__
      return f"{module_name}.{class_name}.__call__"
  
    else:
      # For anything else, fallback to str representation
      return str(callable_obj)
