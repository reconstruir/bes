# bf_checksum progress proposal

## Problem

`bf_checksum_cache.get_checksum()` is the only slow call in `bf_rsync_file_sync._sync_one` that has no feedback. For a 20 GB video file with no cached checksum, a sha256 takes 30–90 seconds. During that time the status line is frozen at `chk_local`. The user cannot tell whether the process is working or hung.

## When is it actually slow?

Only on a cache miss. On a hit — xattr or SQLite — the call completes in milliseconds.

`bf_checksum_cache.has_cached(filename, algorithm)` already exists and answers the question without computing the checksum. The API returns True if and only if a fresh cached value exists. This is the "will it be slow?" gate.

Design rule: **show progress UI if and only if `has_cached()` returns False before calling `get_checksum()`.**

If `has_cached()` returns True and a progress callback is passed anyway (e.g., because of a TOCTOU race where the cache was populated between the two calls), the callback simply never fires. That is the correct outcome — the computation did not happen so there is nothing to report.

## Layer 1 — bf_checksum.checksum()

Add an optional `progress_callback` parameter.

The callback is called once per chunk after the hash is updated. It receives two values: how many bytes have been hashed so far, and the total file size in bytes. Total is computed once at the start via the file size; this lets the callback show a meaningful percent without the caller knowing the size independently.

The call frequency is determined by `chunk_size` (default 1 MB). For a 20 GB file, the callback fires roughly 20,000 times. For a 100 MB file, 100 times. This is plenty of resolution for a progress bar without being expensive.

The `num_chunks` parameter (used for partial-read duplicate detection) interacts badly with progress because `total_bytes` would be the full file size but only a fraction is read. When `num_chunks` is set, the `progress_callback` parameter should be ignored (or callers should simply not pass one). All existing call sites that use `num_chunks` are in duplicate-finding logic that has no progress UI anyway.

When `progress_callback` is None (the default), the code path is identical to today. No performance cost for existing callers.

## Layer 2 — bf_checksum_cache.get_checksum()

Add an optional `progress_callback` parameter. Pass it through to `bf_checksum.checksum()` only on a cache miss.

There are two code paths inside `get_checksum()`:

**xattr path**: Uses a `value_maker` lambda that calls `bf_checksum.checksum()` internally. The lambda is only invoked on a miss. The `progress_callback` must be captured into the lambda at call time so it is forwarded when the lambda fires. On a hit the lambda is never called so the callback never fires.

**database path**: Calls `bf_checksum.checksum()` directly after a failed cache lookup. The `progress_callback` is passed straight through at that call site.

In both paths the rule is: callback fires if and only if a computation actually happens.

`has_cached()` does not need a `progress_callback` parameter — it never computes.

## Layer 3 — bf_rsync_file_sync._sync_one

The call sequence for `chk_local` becomes:

1. Check `has_cached(src, 'sha256')`. Call the result `will_compute`.
2. If `will_compute` and `self._show_progress` are both True, prepare a progress callback that writes the `\r[N/M] size - basename  chk_local  NN%` line.
3. Call `get_checksum(src, 'sha256', progress_callback=...)`. Pass the callback only when both conditions above are met, otherwise None.
4. The `_update_status('chk_local')` call (which today writes a static status line) becomes the fallback for the cached case. It fires when `will_compute` is False: the line flashes briefly as the fast cache lookup completes, then the code immediately advances to `chk_remote`.

Display format for the computing case:

```
[3/47] 18.3G - Movie.Title.2020.mkv  chk_local  47%
```

The percent is derived from `bytes_done / total_bytes * 100` rounded to the nearest integer. No decimal places needed; single-integer updates are readable at normal scrolling speed.

## The 0%-then-100% non-problem

If progress UI is shown only when `has_cached()` returns False, there is no instant jump. The callback fires per chunk throughout the computation. There is no state where 0% appears and then 100% appears with nothing in between.

The only edge case is a very small file (under 1 MB) where there is only one chunk. For a 500 KB file the callback fires once at 100%. That is acceptable — the computation completes in milliseconds anyway and the status line will have already shown `chk_local` briefly before updating.

A size threshold could suppress progress entirely for small files (e.g., under 10 MB). This avoids the cosmetically odd single-shot 100% flash. Suggested threshold: do not pass a progress callback at all when `os.path.getsize(src) < 10 * 1024 * 1024`. The static `chk_local` status label covers this case.

## Other call sites

There are roughly 35 call sites across the codebase that call either `bf_checksum.checksum()` or `bf_checksum_cache.get_checksum()`. All of them work correctly today without progress and will continue to work without change since `progress_callback` defaults to None.

Sites that could optionally benefit in the future:

- `bf_file_mover_worker` (lines 184–185): computes checksums of staging and tmp paths during a move. These are local copies so they can be large. If the file mover ever gets a progress UI, the same `has_cached()`-first pattern applies.
- `bf_metadata_factory_checksum`: batch processing; progress not meaningful per-file since it is already parallel.

No other call site is a candidate for near-term progress.

## Summary of changes

| Layer | What changes |
|---|---|
| `bf_checksum.checksum()` | New optional `progress_callback` param; called per chunk with `(bytes_done, total_bytes)`; no-op when None |
| `bf_checksum_cache.get_checksum()` | New optional `progress_callback` param; forwarded to `bf_checksum.checksum()` only on cache miss; no-op when None |
| `bf_checksum_cache.has_cached()` | No change — already provides the "will it be slow?" answer |
| `bf_rsync_file_sync._sync_one` | Check `has_cached()` first; pass callback only when `will_compute and _show_progress`; add size threshold to skip progress on small files |
| All other call sites | No change |

## What is not proposed

- Per-chunk xattr or SQLite writes during hashing. The cache is written once at the end. Mid-computation caching would require a partial-result format and recovery logic; the complexity is not worth it.
- A `checksum_progress` namedtuple. A plain two-argument callback `(bytes_done, total_bytes)` is sufficient; callers compute percent themselves. Named fields would be added later if other callers need richer metadata.
- Async or threaded hashing. The computation is I/O-bound on the local disk. A background thread would complicate the status line without improving throughput.
- Progress for `bf_checksum_fingerprint.make_key()`. The fingerprint reads only 4096 bytes from head and tail of the file; it is always fast.
