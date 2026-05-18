#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.bf_filename_simplify import bf_filename_simplify

class test_bf_filename_simplify(unit_test):

  # --- simplify_stem ---

  def test_simplify_stem_basic_space(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('hello world'))

  def test_simplify_stem_already_clean(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('hello_world'))

  def test_simplify_stem_uppercase(self):
    self.assertEqual('hello', bf_filename_simplify.simplify_stem('HELLO'))

  def test_simplify_stem_mixed_case(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('Hello World'))

  def test_simplify_stem_multiple_spaces(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('hello  world'))

  def test_simplify_stem_tabs_and_newlines(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('hello\t\nworld'))

  def test_simplify_stem_punctuation_dots(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('hello...world'))

  def test_simplify_stem_punctuation_commas(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('hello, world'))

  def test_simplify_stem_punctuation_exclamation(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('hello world!'))

  def test_simplify_stem_mixed_whitespace_and_punctuation(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('hello,   world!!'))

  def test_simplify_stem_leading_punctuation(self):
    self.assertEqual('hello', bf_filename_simplify.simplify_stem('!!!hello'))

  def test_simplify_stem_trailing_punctuation(self):
    self.assertEqual('hello', bf_filename_simplify.simplify_stem('hello!!!'))

  def test_simplify_stem_surrounding_punctuation(self):
    self.assertEqual('hello', bf_filename_simplify.simplify_stem('(hello)'))

  def test_simplify_stem_numbers(self):
    self.assertEqual('movie_2024', bf_filename_simplify.simplify_stem('Movie (2024)'))

  def test_simplify_stem_numbers_only(self):
    self.assertEqual('2024', bf_filename_simplify.simplify_stem('2024'))

  def test_simplify_stem_hyphens_collapse(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('hello---world'))

  def test_simplify_stem_underscores_collapse(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('hello___world'))

  # western diacritics — stripped via NFKD + Mn removal

  def test_simplify_stem_acute_accent(self):
    self.assertEqual('cafe', bf_filename_simplify.simplify_stem('café'))

  def test_simplify_stem_french_phrase(self):
    self.assertEqual('cafe_au_lait', bf_filename_simplify.simplify_stem('café au lait'))

  def test_simplify_stem_spanish_tilde(self):
    self.assertEqual('el_nino', bf_filename_simplify.simplify_stem('El Niño'))

  def test_simplify_stem_german_umlaut(self):
    self.assertEqual('uber', bf_filename_simplify.simplify_stem('Über'))

  def test_simplify_stem_german_all_umlauts(self):
    self.assertEqual('aouu', bf_filename_simplify.simplify_stem('äöüÜ'))

  def test_simplify_stem_mixed_diacritics(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify_stem('Héllo Wörld'))

  def test_simplify_stem_cedilla(self):
    self.assertEqual('francais', bf_filename_simplify.simplify_stem('français'))

  # non-western scripts pass through (lowercased where applicable)

  def test_simplify_stem_cyrillic(self):
    self.assertEqual('привет_мир', bf_filename_simplify.simplify_stem('Привет мир'))

  def test_simplify_stem_cyrillic_no_spaces(self):
    self.assertEqual('привет', bf_filename_simplify.simplify_stem('Привет'))

  def test_simplify_stem_chinese(self):
    self.assertEqual('中文测试', bf_filename_simplify.simplify_stem('中文测试'))

  def test_simplify_stem_japanese(self):
    self.assertEqual('日本語', bf_filename_simplify.simplify_stem('日本語'))

  def test_simplify_stem_arabic(self):
    self.assertEqual('مرحبا', bf_filename_simplify.simplify_stem('مرحبا'))

  def test_simplify_stem_mixed_latin_and_cyrillic(self):
    self.assertEqual('hello_привет', bf_filename_simplify.simplify_stem('hello привет'))

  def test_simplify_stem_mixed_latin_and_chinese(self):
    self.assertEqual('hello_中文', bf_filename_simplify.simplify_stem('hello 中文'))

  # separator option

  def test_simplify_stem_separator_hyphen(self):
    self.assertEqual('hello-world', bf_filename_simplify.simplify_stem('hello world', separator='-'))

  def test_simplify_stem_separator_hyphen_collapses(self):
    self.assertEqual('hello-world', bf_filename_simplify.simplify_stem('hello...world', separator='-'))

  def test_simplify_stem_separator_hyphen_strips_edges(self):
    self.assertEqual('hello', bf_filename_simplify.simplify_stem('(hello)', separator='-'))

  # idempotency

  def test_simplify_stem_idempotent_plain(self):
    value = 'hello_world_2024'
    self.assertEqual(value, bf_filename_simplify.simplify_stem(value))

  def test_simplify_stem_idempotent_cyrillic(self):
    value = 'привет_мир'
    self.assertEqual(value, bf_filename_simplify.simplify_stem(value))

  # edge cases

  def test_simplify_stem_empty_string(self):
    self.assertEqual('', bf_filename_simplify.simplify_stem(''))

  def test_simplify_stem_all_punctuation(self):
    self.assertEqual('', bf_filename_simplify.simplify_stem('!!!'))

  def test_simplify_stem_all_whitespace(self):
    self.assertEqual('', bf_filename_simplify.simplify_stem('   '))

  def test_simplify_stem_single_letter(self):
    self.assertEqual('a', bf_filename_simplify.simplify_stem('A'))

  # --- simplify ---

  def test_simplify_basic(self):
    self.assertEqual('hello_world.mp4', bf_filename_simplify.simplify('Hello World.mp4'))

  def test_simplify_extension_uppercase(self):
    self.assertEqual('video.mp4', bf_filename_simplify.simplify('video.MP4'))

  def test_simplify_extension_mixed_case(self):
    self.assertEqual('video.mp4', bf_filename_simplify.simplify('video.Mp4'))

  def test_simplify_no_extension(self):
    self.assertEqual('hello_world', bf_filename_simplify.simplify('Hello World'))

  def test_simplify_with_diacritics(self):
    self.assertEqual('cafe_menu.pdf', bf_filename_simplify.simplify('Café Menu.pdf'))

  def test_simplify_cyrillic_basename(self):
    self.assertEqual('привет.mp4', bf_filename_simplify.simplify('Привет.mp4'))

  def test_simplify_chinese_basename(self):
    self.assertEqual('中文.mp4', bf_filename_simplify.simplify('中文.mp4'))

  def test_simplify_real_world_movie(self):
    self.assertEqual('my_movie_2024_final.mp4',
                     bf_filename_simplify.simplify('My Movie (2024) - Final!.mp4'))

  def test_simplify_real_world_spaces_and_dots(self):
    self.assertEqual('some_show_s01e03.mkv',
                     bf_filename_simplify.simplify('Some Show - S01E03.mkv'))

  def test_simplify_separator_hyphen(self):
    self.assertEqual('hello-world.mp4',
                     bf_filename_simplify.simplify('Hello World.mp4', separator='-'))

  def test_simplify_already_clean(self):
    self.assertEqual('video.mp4', bf_filename_simplify.simplify('video.mp4'))

  def test_simplify_idempotent(self):
    name = 'my_movie_2024.mp4'
    self.assertEqual(name, bf_filename_simplify.simplify(name))

  def test_simplify_compound_extension(self):
    # path.splitext only splits the last extension; the intermediate .tar becomes part of the stem
    self.assertEqual('archive_tar.gz', bf_filename_simplify.simplify('Archive.tar.GZ'))

  # error cases

  def test_simplify_path_separator_raises(self):
    with self.assertRaises(ValueError):
      bf_filename_simplify.simplify('dir/file.mp4')

  def test_simplify_empty_stem_raises(self):
    with self.assertRaises(ValueError):
      bf_filename_simplify.simplify('!!!!!.mp4')

  def test_simplify_all_punctuation_no_extension_raises(self):
    with self.assertRaises(ValueError):
      bf_filename_simplify.simplify('!!!')

if __name__ == '__main__':
  unit_test.main()
