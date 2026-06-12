# bes/fs → bes/files migration plan

## Scope

Make `lib/bes/fs/` files that have `bf_`-prefixed counterparts in
`lib/bes/files/` delegate to those counterparts internally, keeping their
existing public API intact.  This is a **semantics-only** phase: no callers
change, nothing in `fs/` is deleted, and no new `bf_` files are created.

## Model: how file_find.py already does it

`fs/file_find.py` is the reference pattern.  It keeps every old classmethod
(`find`, `find_function`, `find_fnmatch`, `find_re`, …) but their bodies
now build a `bf_file_finder_options` object, call
`bf_file_finder.find_with_options()`, and post-process the result into the
old return type (a plain list of relative or absolute filenames).  The public
surface is unchanged; the old implementation is gone.

`fs/file_mime.py` uses the even simpler pattern: `class file_mime(bf_mime): pass`.
Use whichever fits.

---

## Files to migrate (priority order)

### 1. `file_resolver.py` → `bf_file_resolver`

This is the main target.  It is also the most complex because of the option
and return-type gaps.

**Semantic gaps to resolve before writing code:**

| Concern | Old (`file_resolver`) | New (`bf_file_resolver`) |
|---|---|---|
| API shape | classmethods | instance, `__init__(options)` |
| Return type | `file_resolver_item_list` of `file_resolver_item` namedtuples | `bf_entry_list` of `bf_file_resolver_entry` objects |
| `recursive` flag | `options.recursive` → `max_depth=1` or `None` | `options.max_depth` directly |
| `limit` | `options.limit` (post-filter slice) | `options.stop_after` |
| `sort_order` | `file_sort_order` enum (DATE, DEPTH, FILENAME, SIZE) | `bf_entry_sort_criteria` enum (MODIFICATION_DATE, FILENAME, SIZE, …) |
| match options | `match_patterns`, `match_re`, `match_type`, `match_basename`, `match_function` | `match_function` only (pattern matching goes through `bf_file_matcher`) |
| ignore | `ignore_files: list[str]` via `file_ignore_options_mixin` | `ignore_filename: str` (single filename) |

**Approach:**

`file_resolver.resolve_files()` and `resolve_dirs()` are classmethods — keep
that.  Inside each, translate old `file_resolver_options` fields to
`bf_file_resolver_options`, instantiate `bf_file_resolver`, call
`resolver.resolve(files)`, then convert `bf_entry_list` →
`file_resolver_item_list` by constructing `file_resolver_item` from each
`bf_file_resolver_entry`'s `filename`, `root_dir`, `index`, `found_index`.

Translation notes:
- `recursive=True` → `max_depth=None`; `recursive=False` → `max_depth=1`
- `limit` → `stop_after` (bf uses stop_after to cap scanning, old used a
  post-filter slice; semantics are close enough for this phase)
- `sort_order` mapping: `file_sort_order.FILENAME` → `bf_entry_sort_criteria.FILENAME`,
  `file_sort_order.SIZE` → `bf_entry_sort_criteria.SIZE`,
  `file_sort_order.DATE` → `bf_entry_sort_criteria.MODIFICATION_DATE`,
  `file_sort_order.DEPTH` — no direct equivalent in bf yet, keep old sort
  fallback for this value only
- `match_function` passes through as-is (both take a single entry argument —
  note bf passes a `bf_entry`; ensure callers that used `file_resolver_item`
  fields are updated or the conversion wraps correctly)
- `match_patterns`, `match_re`, `match_type`, `match_basename` — build a
  `bf_file_matcher` from these and pass as `match_function`
- `ignore_files` list — bf supports only a single `ignore_filename`; for now,
  use `ignore_files[0]` if the list has exactly one entry, otherwise fall back
  to the old `file_ignore` logic wrapped in a `match_function`

### 2. `file_resolver_options.py` — no separate action needed

`file_resolver_options` is already a `bcli_options` subclass.  It stays as
the public-facing options class; the delegation layer in `file_resolver.py`
converts it to `bf_file_resolver_options` internally.

### 3. `file_ignore.py` → `bf_file_ignore`

`file_ignore` and `bf_file_ignore` have the same interface
(`should_ignore(ford)`).  Make `file_ignore` delegate constructor and
`should_ignore` to `bf_file_ignore`.

### 4. `file_ignore_item.py` → `bf_file_ignore_item`

`file_ignore_item` is a namedtuple `(directory, patterns)`.
`bf_file_ignore_item` has the same shape.  Subclass or alias:

```python
from bes.files.ignore.bf_file_ignore_item import bf_file_ignore_item
class file_ignore_item(bf_file_ignore_item):
    pass
```

Verify `read_file` classmethod still works.

### 5. `file_multi_ignore.py` → `bf_file_multi_ignore`

Same pattern as `file_ignore`: delegate `__init__` and `should_ignore` to
`bf_file_multi_ignore`.  Or subclass directly if the constructor signatures
match.

### 6. `file_type.py` → `bf_file_type`

`file_type` uses integer bit flags (BLOCK=1, CHAR=2, DIR=4, FILE=8, LINK=16).
`bf_file_type` is a `checked_enum`.  These are not directly compatible.

The translation layer in `file_find.py` already handles this (it maps
`file_find.FILE` etc. to `bf_file_type` values).  For `file_type.py` itself:

- Leave the class constants in place for now (callers use them as literals)
- Add a classmethod `to_bf_file_type(flags)` that converts the old bitmask
  to a `bf_file_type` value, for use by delegating code in `file_find` and
  `file_resolver`

This is a semantics-only note — no caller changes.

### 7. `temp_file.py` → `bf_temp_file`

`temp_file` is a rich class (temp files, temp dirs, populated dirs for
testing).  `bf_temp_file` covers only simple temp-file creation.  Check
which methods overlap and delegate those; leave the rest in place.

---

## Files NOT in scope for this phase

These `fs/` files have no `bf_` counterpart yet, or the counterpart is
sufficiently different that a semantics-only pass is not straightforward:

- `file_search.py`, `file_replace.py`, `file_sync.py`, `file_copy.py`
- `file_match.py` (used internally by `file_find`; covered by `bf_file_matcher`)
- `file_attributes*.py`, `file_checksum_getter_*.py`
- `file_cache.py`, `file_mode.py`, `file_open.py`
- `compressed_file.py`, `tar_util.py`, `xcopy.py`, `dir_cleanup.py`
- `dir_combine.py`, `dir_partition.py`, `dir_split.py` (already have bf_ command
  factories but the core logic files differ)
- `filename_list.py`, `filename_util.py`

---

## Order of work

1. **`file_resolver.py`** — highest value, most callers, hardest semantics.
   Do this first and run the full test suite immediately after.
2. **`file_ignore.py` / `file_ignore_item.py` / `file_multi_ignore.py`** —
   low risk, do together.
3. **`temp_file.py`** — audit overlap first.
4. **`file_type.py`** — add `to_bf_file_type()` helper only; no behaviour change.

---

## Testing strategy

- Run `./t tests/lib/bes/fs/` after each file.
- `file_resolver` changes will also surface failures in any project that uses
  `file_resolver` directly — run the full bes suite and spot-check rmt/rehack.
- The public API of every migrated file must remain identical; if a test
  breaks it is a semantic regression, not an acceptable trade-off.
