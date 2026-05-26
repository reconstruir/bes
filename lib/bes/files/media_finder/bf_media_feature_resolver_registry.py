#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bf_media_feature_resolver_registry:
  'Name → class registry for bf_media_feature_resolver_base subclasses.'

  _registry = {}

  @classmethod
  def register(cls, resolver_class):
    'Register a resolver class keyed by its name attribute.'
    cls._registry[resolver_class.name] = resolver_class

  @classmethod
  def get(cls, name):
    'Return the resolver class for name. Raises KeyError if not registered.'
    return cls._registry[name]

  @classmethod
  def names(cls):
    'Return a list of all registered resolver names.'
    return list(cls._registry.keys())
