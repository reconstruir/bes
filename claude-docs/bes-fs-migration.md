# bes.fs → bes.files Migration Status

## Goal

Eliminate all `bes.fs` imports from `bav`, `rapp`, and `rmt` in favour of `bes.files` equivalents.

---

## Completed

| bes.fs symbol | bes.files replacement | Notes |
|---|---|---|
| `temp_file` / `temp_item` | `bes.files.bf_temp_file` / `bf_temp_item` | ~150 callers migrated |
| `file_mime` | `bes.files.mime.bf_mime` | all callers migrated |
| `filename_util` | `bes.files.bf_filename` | all callers migrated |
| `file_entry` | removed | `rui_media_list_entry` never actually used it |
| `file_entry_list` | `bes.files.bf_entry_list` | `rui_media_list_entry_list` updated |
| `file_media` | `bes.files.mime.bf_mime_media` | all callers migrated |
| `file_resolver` | `bes.files.resolve.bf_file_resolver` | all direct callers migrated; `bav_file_resolver` internals updated |
| `file_resolver_options` (handler files) | `bes.files.resolve.bf_file_resolver_options` | migrated in CLI handlers; still present in CLI *options* mixins (see blocked) |
| `file_attributes` (testing + ffmpeg) | `bes.files.attr.bf_attr` | 4 callers migrated |
| `file_sort_order` | `bes.files.bf_entry_sort_criteria` | `fdui_file_operations.py` migrated; `bav_file_resolver` type check updated |
| `file_find` (gallery_dl_fetch) | `bes.files.find.bf_file_finder` | migrated |

**Files git-rm'd from bes.fs (no remaining callers):**
- `file_entry.py`, `file_entry_list.py`, `file_media.py`, `file_mime_type_detector.py`,
  `file_checksum_getter_attributes.py`, `device_info.py`

---

## Blocked — No bes.files Equivalent Exists

These need new classes created in `bes.files` before callers can be migrated.

### `dir_operation_item` / `dir_operation_item_list` (14 import lines, 7 files)

**What it does:** Represents a (src, dst) file-move pair. `dir_operation_item_list` batches them and has `.move_files(timestamp, group_id, touch=True)`.

**Callers:** `fdui_main_window`, `fdui_file_tasks`, `file_ops/_op_move`, `post_processor`, `rept_cli_handler`, `rept_gallery_dl`, `gallery_dl_fetch`

**Proposed home:** `bes.files.move` — check if `bf_file_mover_operation` covers this or create `bf_dir_operation_item` / `bf_dir_operation_item_list` as thin wrappers.

---


### `dir_partition` / `dir_partition_options` / `dir_partition_criteria_base` (3 files)

**What it does:** Partitions files in a directory tree into subdirs by criteria (media type, date prefix, etc.).

**Callers:** `rept_reorg`, `rept_reorg_partition_criteria`

**Proposed home:** `bes.files.partition.*` (new subpackage). Low priority — only used by `rept`.

---

### `dir_split` / `dir_split_options` (1 file)

**What it does:** Splits a flat directory of N files into batches of M subdirectories.

**Callers:** `rept_reorg`

**Proposed home:** `bes.files.split.*` (new subpackage). Low priority.

---

### `file_split` / `file_split_options` (2 files)

**What it does:** Splits a large file into numbered parts; `is_split_filename(path)` detects them.

**Callers:** `vb_cli_handler`, `vb_handler`

**Proposed home:** `bes.files.split.bf_file_split`. Low priority.

---

### `temp_content` (1 file, testing only)

**What it does:** Testing helper; creates temp files with specific content for tests.

**Callers:** `rapp/graphics/rapp_temp_media.py`

**Proposed home:** `bes.files.bf_temp_file` — extend with content helpers, or just inline the logic.

---

## Blocked — Different Class Hierarchy (Needs Rearchitecting)

These cannot be swapped 1:1 because the old and new classes are architecturally different.

### `file_attributes_metadata` + `file_metadata_getter_base` (19 import lines)

**The old system (`bes.fs`):**
- `file_metadata_getter_base`: ABC with `name()`, `get_value(manager, filename)`, `decode_value(bytes)`. Subclasses compute one metadata attribute (durations, faces, framerates, etc.) by running an expensive operation and returning a bytes blob.
- `file_attributes_metadata`: registry of getter classes. `register_getter(cls)` at class body time. `get_value(filename, key, fallback, cached)` dispatches to the right getter, stores result as xattr, uses mtime-based caching. Also has `remove_value`, `remove_values`, `get_checksum_*`, `get_mime_type`.
- `bav_file_attributes` inherits from `file_attributes_metadata` and registers 7 getters at class definition time.

**The new system (`bes.files`):**
- `bf_attr_getter_base`: concrete xattr wrapper (has_key, get_bytes, set_bytes, remove, keys, clear). Not an ABC for computed values — it's the storage layer.
- `bf_attr_getter_mixin`: adds typed accessors (get_string, set_string, get_bool, etc.) on top of the storage layer.
- These are **not** a replacement for `file_attributes_metadata`'s dispatch/registry/caching system.

**Relationship to `file_attributes`:** `file_attributes_metadata` uses `file_attributes` internally as its raw xattr storage layer. The two are distinct: `file_attributes` is just get/set of named byte blobs; `file_attributes_metadata` is the dispatch/cache/registry system built on top. Migrating the 20 callers of `file_attributes` to `bf_attr` is independent of and easier than this item.

**What's needed:** Rewrite `bav_file_attributes` and all its getters to use the `bes.files.metadata` subpackage, which is the intended modern equivalent:

- `file_metadata_getter_base` → implement `bf_metadata_factory_base` instead (same contract: one getter per metadata key, compute-on-demand, result stored as xattr bytes)
- `file_attributes_metadata` registry + caching → replaced by `bf_metadata_store` / `bf_metadata_factory_registry`
- `bav_file_attributes` (inherits from `file_attributes_metadata`, registers 7 getters) → rewrite to instantiate `bf_metadata_store` and register `bf_metadata_factory_base` subclasses

**Steps:**
1. Read `bes/files/metadata/bf_metadata_store.py` and `bf_metadata_factory_base.py` to confirm the API.
2. Rewrite each `bav/lib/bav/base/bav_file_metadata_getter_*.py` to subclass `bf_metadata_factory_base` instead of `file_metadata_getter_base`.
3. Rewrite `bav_file_attributes` to use `bf_metadata_store` / `bf_metadata_factory_registry` instead of inheriting from `file_attributes_metadata`.
4. Delete `bes/fs/file_attributes_metadata.py` and `bes/fs/file_metadata_getter_base.py`.

**Affected files:** `bav_file_attributes`, `bav_file_metadata_getter_durations`, `bav_file_metadata_getter_faces` (×4), `bav_file_metadata_getter_framerates`, `bav_file_metadata_getter_num_frames`, `bav_file_metadata_getter_quality_brisque_v1`, `fd_detect`, `opencv_image`, `checksum_db_cli_handler`, `fdui_dir_find_operations`, `firefox_cli_handler`, `image_search`, `rept_cli_handler`, `rept_gallery_dl`

---

### `file_resolver_options` in CLI options mixins (4 import lines)

**The situation:** `post_process_cli_options`, `reddit_cli_options`, `rept_cli_options`, `similar_images_options` all inherit from `file_ignore_options_mixin` (which also needs migration) and store a `file_resolver_options` sub-object for sort/limit/recursive fields. These feed through `bav_file_resolver` whose internals now use `bf_file_resolver`. The mismatch is that callers may pass `file_sort_order` values via these option objects, but `bav_file_resolver` now type-checks for `bf_entry_sort_criteria`.

**Fix:** After `file_ignore_options_mixin` is ported, update these option classes to use `bf_file_resolver_options` or just individual fields (`recursive`, `sort_order` as `bf_entry_sort_criteria`, `limit`).

---

## Completed (second wave)

| bes.fs symbol | bes.files replacement | Notes |
|---|---|---|
| `file_multi_ignore` | `bes.files.ignore.bf_file_multi_ignore` | new class created; 3 direct callers + `bav_file_resolver` type-check migrated |
| `file_ignore_options_mixin` | `bes.files.bf_file_ignore_options_mixin` | new class created; all 11 callers migrated (5 bav + 6 rmt options classes) |
| `file_resolver_options` (dead properties) | removed | `post_process_cli_options`, `similar_images_options`, `reddit_cli_options`, `rept_cli_options` — property was never accessed externally |
| `temp_content` | deleted | `rapp_temp_media.py` was the only caller; file deleted from `bes/fs/` with no replacement needed. 0 callers remaining. |

**Also fixed:** `similar_images.py` and `rept_cli_handler.py` were passing `options.file_ignorer` (bound method) where the instance was needed — now both call `options.file_ignorer()`.

---

## Remaining Import Count by Symbol

As of 2026-06-14 (lib + test files; excludes `bes/lib/bes/fs/` itself):

| Symbol | Files | Notes |
|---|---|---|
| `file_find` | 35+ lib | `file_find.py` already delegates to `bf_file_finder` internally; callers still work but should eventually import `bf_file_finder` directly. Spread across rebuild (20+), eca (6), rehack (4), bat (3), rmt (2), bav, rapp, bes internal. |
| `file_attributes` | 20 | Simple xattr get/set (not the metadata system). bat (2), bav (2), bnet (1), eca (1), rebuild (3), rem_pdf (2), rmusic (1), rmt (3), bes tests (2), other tests (3). |
| `file_attributes_metadata` | 11 | — |
| `file_metadata_getter_base` | 10 | — |
| `dir_operation_item` | 9 | — |
| `dir_operation_item_list` | 9 | — |
| `file_duplicates_options` | 7 | — |
| `file_duplicates` | 5 | — |
| `dir_partition` | 3 | — |
| `dir_split` | 3 | — |
| `file_split` | 4 | rmt/vb only (lib: 2, tests: 2) |
| **Total** | | **~116** |

---

## Suggested Order When Resuming

1. **`dir_operation_item` / `dir_operation_item_list`** → `bes.files.move` (check `bf_file_mover_operation`; create `bf_dir_operation_item` / `bf_dir_operation_item_list` if needed; unblocks 9 files)
2. **`file_attributes_metadata` + `file_metadata_getter_base`** → port or rewrite onto `bes.files.metadata`; highest impact (unblocks all `bav_file_metadata_getter_*` and `bav_file_attributes`)
3. **`file_duplicates` / `file_duplicates_options`** → adapt callers to `bf_file_duplicates_finder` API
4. **`file_attributes`** → migrate 20 callers from `bes.fs.file_attributes` to `bes.files.attr.bf_attr`; blocked on auditing each caller's API usage
5. **`file_find`** → large surface (35+ callers), but `file_find.py` already delegates so not urgent; batch-migrate when doing a rebuild/eca pass
6. **`dir_partition` / `dir_split` / `file_split`** → low priority; only used by `rept` and `vb`
