#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

@dataclasses.dataclass
class bf_media_finder_callbacks:
  on_scan_progress: typing.Callable = None  # (found: int, scanned: int)
  on_scan_done:     typing.Callable = None  # (entries: list[bf_media_file_entry])
  on_cancel:        typing.Callable = None  # ()
  on_state_changed: typing.Callable = None  # (state: bf_media_finder_state)
  on_error:         typing.Callable = None  # (exc: Exception)
