#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property

from .unit_test_media import unit_test_media

class unit_test_media_files(object):

  @cached_property
  def png_file(self):
    return self.make_temp_file(content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.png')
  
  @cached_property
  def png_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.txt')

  @cached_property
  def unknown_file_png_extension(self):
    return self.make_temp_file(content = unit_test_media.UNKNOWN, suffix = '.png')

  @cached_property
  def jpg_file(self):
    return self.make_temp_file(content = unit_test_media.JPG_SMALLEST_POSSIBLE, suffix = '.jpg')
  
  @cached_property
  def jpg_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.JPG_SMALLEST_POSSIBLE, suffix = '.txt')

  @cached_property
  def unknown_file_jpg_extension(self):
    return self.make_temp_file(content = unit_test_media.UNKNOWN, suffix = '.jpg')

  @cached_property
  def mp4_file(self):
    return self.make_temp_file(content = unit_test_media.MP4_SMALLEST_POSSIBLE, suffix = '.mp4')

  @cached_property
  def unknown_file_mp4_extension(self):
    return self.make_temp_file(content = unit_test_media.UNKNOWN, suffix = '.mp4')
  
  @cached_property
  def mp4_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.MP4_SMALLEST_POSSIBLE, suffix = '.txt')

  @cached_property
  def unknown_file(self):
    return self.make_temp_file(content = unit_test_media.UNKNOWN, suffix = '.notaknownext')
  
  @cached_property
  def unknown_file_txt_extension(self):
    return self.make_temp_file(content = unit_test_media.UNKNOWN, suffix = '.txt')
  
  @cached_property
  def zip_file(self):
    return self.make_temp_file(content = unit_test_media.ZIP, suffix = '.zip')
  
  @cached_property
  def zip_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.ZIP, suffix = '.txt')

  @cached_property
  def unknown_file_zip_extension(self):
    return self.make_temp_file(content = unit_test_media.UNKNOWN, suffix = '.zip')

  @cached_property
  def xz_file(self):
    return self.make_temp_file(content = unit_test_media.XZ, suffix = '.xz')
  
  @cached_property
  def xz_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.XZ, suffix = '.txt')

  @cached_property
  def unknown_file_xz_extension(self):
    return self.make_temp_file(content = unit_test_media.UNKNOWN, suffix = '.xz')
  
  @cached_property
  def windows_exe_file(self):
    return self.make_temp_file(content = unit_test_media.WINDOWS_EXE, suffix = '.exe')
  
  @cached_property
  def windows_exe_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.WINDOWS_EXE, suffix = '.txt')

  @cached_property
  def unknown_file_windows_exe_extension(self):
    return self.make_temp_file(content = unit_test_media.UNKNOWN, suffix = '.exe')
  
  @cached_property
  def wav_file(self):
    return self.make_temp_file(content = unit_test_media.WAV_SMALLEST_POSSIBLE, suffix = '.wav')

  @cached_property
  def mp3_file(self):
    return self.make_temp_file(content = unit_test_media.MP3_SMALLEST_POSSIBLE, suffix = '.mp3')

  @cached_property
  def flac_file(self):
    return self.make_temp_file(content = unit_test_media.FLAC_SMALLEST_POSSIBLE, suffix = '.flac')
  
