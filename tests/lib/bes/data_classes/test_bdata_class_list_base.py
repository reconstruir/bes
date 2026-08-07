#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import base64
import dataclasses
import pickle
from unittest.mock import patch

from bes.testing.unit_test import unit_test

from bes.data_classes.bdata_class_base import bdata_class_base
from bes.data_classes.bdata_class_list_base import bdata_class_list_base

@dataclasses.dataclass(order=True)
class _fake_item(bdata_class_base):

  name: str
  value: int

class _fake_item_list(bdata_class_list_base):

  __value_type__ = _fake_item

_fake_item_list.register_check_class()

class test_bdata_class_list_base(unit_test):

  _TEST_LIST = _fake_item_list([
    _fake_item('one', 1),
    _fake_item('two', 2),
  ])

  def test_to_pickle_protocol_is_pinned(self):
    '''
    pickle.DEFAULT_PROTOCOL varies by Python version (4 through 3.13, 5
    starting in 3.14) -- to_pickle() must not depend on it, or output
    (and any hardcoded-fixture test comparing against it, like
    bnet's test_web_proxy_recording_item_list) silently changes shape
    when the interpreter changes.  Protocol 2+ pickles start with the
    PROTO opcode (0x80) followed by the protocol number byte.
    '''
    pickled = self._TEST_LIST.to_pickle()
    self.assertEqual( b'\x80\x05', pickled[0:2] )

  def test_to_pickle_protocol_is_pinned_regardless_of_default(self):
    'Same as above, but proves it even when DEFAULT_PROTOCOL is forced to something else, so this actually catches the pin being accidentally removed.'
    with patch('pickle.DEFAULT_PROTOCOL', 4):
      pickled = self._TEST_LIST.to_pickle()
      self.assertEqual( b'\x80\x05', pickled[0:2] )

  def test_pickle_round_trip(self):
    pickled = self._TEST_LIST.to_pickle()
    result = _fake_item_list.read_pickle_bytes(pickled, 'test')
    self.assertEqual( self._TEST_LIST, result )

  def test_base64_pickle_round_trip(self):
    b64 = self._TEST_LIST.to_base64_pickle()
    result = _fake_item_list.read_pickle_bytes(base64.b64decode(b64), 'test')
    self.assertEqual( self._TEST_LIST, result )
