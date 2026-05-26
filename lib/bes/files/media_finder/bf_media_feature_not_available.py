#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class _bf_feature_not_available_type:
  'Singleton sentinel returned by resolvers when a file has no data for the requested feature.'
  _instance = None

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  def __bool__(self):
    return False

  def __repr__(self):
    return 'BF_FEATURE_NOT_AVAILABLE'

  def __eq__(self, other):
    return isinstance(other, _bf_feature_not_available_type)

  def __hash__(self):
    return hash('_bf_feature_not_available_type')

BF_FEATURE_NOT_AVAILABLE = _bf_feature_not_available_type()
