#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bf_file_mover_options:

  def __init__(self,
               chunk_size=None,
               verify_checksum_after_copy=False,
               on_progress=None,
               on_complete=None,
               on_pause=None):
    self.chunk_size = chunk_size or (4 * 1024 * 1024)
    self.verify_checksum_after_copy = verify_checksum_after_copy
    self.on_progress = on_progress
    self.on_complete = on_complete
    self.on_pause = on_pause
