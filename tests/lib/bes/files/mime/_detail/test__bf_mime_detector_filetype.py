#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip

from _bf_mime_type_detector_tester import make_test_case

from bes.files.mime._detail._bf_mime_type_detector_filetype import _bf_mime_type_detector_filetype

class test__bf_mime_detector_filetype(make_test_case(_bf_mime_type_detector_filetype)):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if(_bf_mime_type_detector_filetype.is_supported(), 'filetype not found')

  # filetype is binary-signatures only; text-based formats return None

  def test_text_plain(self):
    tmp = self.make_temp_file(content = 'this is text\n', suffix = '.txt')
    self.assertIsNone(_bf_mime_type_detector_filetype.detect_mime_type(tmp))

  def test_xml(self):
    tmp = self.make_temp_file(content = '<?xml version="1.0"?>\n<root/>\n', suffix = '.xml')
    self.assertIsNone(_bf_mime_type_detector_filetype.detect_mime_type(tmp))

  def test_html(self):
    tmp = self.make_temp_file(content = '<!DOCTYPE html>\n<html><body></body></html>\n', suffix = '.html')
    self.assertIsNone(_bf_mime_type_detector_filetype.detect_mime_type(tmp))

  def test_json(self):
    tmp = self.make_temp_file(content = '{"key": "value"}\n', suffix = '.json')
    self.assertIsNone(_bf_mime_type_detector_filetype.detect_mime_type(tmp))

if __name__ == '__main__':
  unit_test.main()
