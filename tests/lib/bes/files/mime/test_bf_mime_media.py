#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.mime.bf_mime_media import bf_mime_media

class test_bf_mime_media(unit_test):

  def test_image_extensions_contains_common(self):
    for ext in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
      self.assertIn(ext, bf_mime_media.IMAGE_EXTENSIONS)

  def test_video_extensions_contains_common(self):
    for ext in ('mp4', 'mov', 'avi', 'mkv', 'webm'):
      self.assertIn(ext, bf_mime_media.VIDEO_EXTENSIONS)

  def test_audio_extensions_contains_common(self):
    for ext in ('mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'aiff', 'wma', 'opus'):
      self.assertIn(ext, bf_mime_media.AUDIO_EXTENSIONS)

  def test_extensions_is_union_of_all_three(self):
    expected = bf_mime_media.IMAGE_EXTENSIONS | bf_mime_media.VIDEO_EXTENSIONS | bf_mime_media.AUDIO_EXTENSIONS
    self.assertEqual(expected, bf_mime_media.EXTENSIONS)

  def test_image_and_video_disjoint(self):
    self.assertEqual(frozenset(), bf_mime_media.IMAGE_EXTENSIONS & bf_mime_media.VIDEO_EXTENSIONS)

  def test_image_and_audio_disjoint(self):
    self.assertEqual(frozenset(), bf_mime_media.IMAGE_EXTENSIONS & bf_mime_media.AUDIO_EXTENSIONS)

  def test_video_and_audio_disjoint(self):
    self.assertEqual(frozenset(), bf_mime_media.VIDEO_EXTENSIONS & bf_mime_media.AUDIO_EXTENSIONS)

  def test_mime_type_to_extension_image(self):
    self.assertEqual('jpg',  bf_mime_media.mime_type_to_extension('image/jpeg'))
    self.assertEqual('png',  bf_mime_media.mime_type_to_extension('image/png'))
    self.assertEqual('gif',  bf_mime_media.mime_type_to_extension('image/gif'))

  def test_mime_type_to_extension_video(self):
    self.assertEqual('mp4',  bf_mime_media.mime_type_to_extension('video/mp4'))
    self.assertEqual('mov',  bf_mime_media.mime_type_to_extension('video/quicktime'))
    self.assertEqual('mkv',  bf_mime_media.mime_type_to_extension('video/x-matroska'))

  def test_mime_type_to_extension_audio(self):
    self.assertEqual('mp3',  bf_mime_media.mime_type_to_extension('audio/mpeg'))
    self.assertEqual('flac', bf_mime_media.mime_type_to_extension('audio/flac'))
    self.assertEqual('wav',  bf_mime_media.mime_type_to_extension('audio/wav'))
    self.assertEqual('wav',  bf_mime_media.mime_type_to_extension('audio/x-wav'))
    self.assertEqual('wav',  bf_mime_media.mime_type_to_extension('audio/wave'))
    self.assertEqual('aac',  bf_mime_media.mime_type_to_extension('audio/aac'))
    self.assertEqual('ogg',  bf_mime_media.mime_type_to_extension('audio/ogg'))
    self.assertEqual('m4a',  bf_mime_media.mime_type_to_extension('audio/mp4'))
    self.assertEqual('wma',  bf_mime_media.mime_type_to_extension('audio/x-ms-wma'))
    self.assertEqual('aiff', bf_mime_media.mime_type_to_extension('audio/aiff'))
    self.assertEqual('aiff', bf_mime_media.mime_type_to_extension('audio/x-aiff'))

  def test_mime_type_to_extension_unknown(self):
    self.assertIsNone(bf_mime_media.mime_type_to_extension('application/json'))

if __name__ == '__main__':
  unit_test.main()
