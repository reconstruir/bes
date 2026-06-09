#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.files.metadata.bf_metadata import bf_metadata

class unit_test_bf_metadata_mixin:
  'Mixin that redirects the metadata DB to a per-test temp dir to avoid HOME side effects.'

  def setUp(self):
    super().setUp()
    self._metadata_test_dir = self.make_temp_dir()
    os.environ['BES_METADATA_DIR'] = self._metadata_test_dir
    bf_metadata.reset()

  def tearDown(self):
    super().tearDown()
    os.environ.pop('BES_METADATA_DIR', None)
    bf_metadata.reset()
