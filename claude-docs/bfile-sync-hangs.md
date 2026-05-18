# bfile-sync hang handling — proposal

---

## Root cause analysis

### What `execute.execute` does today

`system_command.call_command` → `execute.execute` → `process.communicate()` with **no timeout**.
`communicate()` blocks until the subprocess exits, forever if it never does.

### Why the hang happened

The most likely scenario given "partial file was done, size and checksum not changing":
rsync completed the data transfer over the SSH pipe but the SSH connection itself
became unresponsive before the channel could be closed cleanly. rsync was waiting
for the SSH session to finish; SSH was waiting for the NAS to acknowledge; nothing
was timing out on either side.

### Three failure modes to cover

| Mode | Where it hangs | Symptom |
|------|---------------|---------|
| **Mid-transfer I/O stall** | rsync, inside the transfer | File size grows then stops, rsync still running |
| **Post-transfer SSH channel hang** | rsync waiting for SSH close | File size stable, rsync still running — *the observed case* |
| **SSH command hang** | `sha256sum`, `mkdir -p`, `cleanup` | Program appears stuck between rsync calls |

---

## Defence layers

Two layers are sufficient. A third process-level kill is redundant because
`ServerAliveInterval`/`ServerAliveCountMax` IS SSH's built-in process timeout — when
the probes go unanswered SSH kills itself and exits non-zero, which is exactly what a
`communicate(timeout=N)` + SIGKILL would do but at the protocol level where it's more
precise. `ConnectTimeout` covers the connection-establishment case that keepalives
cannot (no connection yet to send probes over).

### Layer 1 — rsync `--timeout=N` (I/O idle timeout)

rsync has a built-in `--timeout=SECONDS` option: if no data is transferred for N
seconds, rsync exits with an error. Handles mid-transfer I/O stalls but **does not**
help with post-transfer SSH channel hangs (no I/O is expected after the transfer
completes, so the timer never fires).

Recommended value: **300 seconds** (5 min). Covers slow-start or throttled transfers
without false positives on large files.

Add to `_rsync` in `bf_rsync_file_sync`:
```python
cmd = [
  '--partial', '--partial-dir=.rsync-partial',
  '--exclude=**/.DS_Store',
  '--human-readable', '--stats',
  '--timeout=300',    # ← new
  '-va',
  ...
]
```

### Layer 2 — SSH keepalive and connection-timeout flags

Three SSH options, applied to every SSH invocation:

| Option | Value | Purpose |
|--------|-------|---------|
| `ConnectTimeout` | 30 s | Caps connection establishment; covers DNS/TCP hangs before SSH is up |
| `ServerAliveInterval` | 30 s | Send keepalive probe every 30 s of silence |
| `ServerAliveCountMax` | 3 | Give up after 3 unanswered probes (90 s total silence budget) |

**Total silence budget for any SSH session: 90 seconds.**

These are applied in two places:

**rsync `-e ssh ...` string** — affects the SSH session rsync runs over:
```
ssh -i {key} -o BatchMode=yes -o ConnectTimeout=30
    -o ServerAliveInterval=30 -o ServerAliveCountMax=3 ...
```

**All `bssh_command` calls** (`sha256sum`, `mkdir -p`, `cleanup`) — same three
options added to `ssh_args`. Currently each method builds `ssh_args` independently
with the same boilerplate. Extract a `_ssh_args()` helper that returns the full base
args list so the timeout options are set in one place.

---

## Retry behaviour (already correct)

When either timeout fires, the exception propagates out of `_sync_one`,
gets caught by the `_run_loop` error handler, emits a `RETRY` line, sleeps
`retry_wait_seconds`, and retries the file. rsync `--partial` + `--partial-dir`
means the next attempt resumes from where the previous left off — exactly what
was observed when the program was restarted manually.

**No changes needed to retry logic.**

---

## Configuration

| Setting | Default | Expose as parameter? |
|---------|---------|---------------------|
| rsync `--timeout` | 300 s | No — hardcode; rarely needs tuning |
| SSH `ConnectTimeout` | 30 s | No |
| SSH `ServerAliveInterval` | 30 s | No |
| SSH `ServerAliveCountMax` | 3 | No |

None of these need to be user-tunable for this use case.

---

## Open issues

1. **SSH keepalive requires server support**: `ServerAliveInterval` is a client-side
   keepalive; TrueNAS (OpenSSH) supports it by default. No server-side config needed.

2. **rsync `--timeout` vs SSH keepalive interaction**: if `--timeout=300` fires
   first, rsync exits and the SSH channel closes normally. If the SSH keepalive
   fires first (90 s), SSH exits and rsync gets a broken pipe. Both produce a
   non-zero exit code; both are caught by the retry loop. No conflict.

3. **Process-level timeout for rsync deliberately omitted**: A 100 GB file at
   100 MB/s takes ~17 min. Any fixed wall-clock timeout would false-positive on
   large files or slow links. Layers 1 and 2 are sufficient.

---

## Implementation plan

1. Add `_ssh_args()` instance method to `bf_rsync_file_sync` returning the full
   base SSH args list with all timeout options. Replaces the repeated boilerplate
   in `_ssh_sha256`, `_ssh_mkdir`, `_cleanup_partial`.

2. Add `_rsync_ssh_command()` instance method returning the `-e ssh ...` string
   for rsync with the same timeout options.

3. Add `--timeout=300` to the rsync args in `_rsync`.

4. Update `_ssh_sha256`, `_ssh_mkdir`, `_cleanup_partial` to call `_ssh_args()`.

No changes to `execute.execute` or `system_command.call_command`.

---

## Checksum optimization (future work — independent)

### Problem

`sha256sum` runs over SSH on the NAS *twice* per file:

1. **Pre-transfer** — to decide skip vs transfer (reads the full remote file)
2. **Post-transfer** — to verify integrity (reads the full transferred file)

For large video files on spinning NAS disks (~100–200 MB/s read), each pass takes
**2–5 minutes**. During this time the progress display shows `filename ...` and
nothing changes — indistinguishable from a hang.

### Proposal: stat-first pre-transfer check

Before computing the remote SHA-256, run a fast `stat` (or `ls -l`) over SSH to get
the remote file size. Compare against the local file size:

- **Sizes differ** → different content with certainty → skip the remote SHA-256,
  go straight to rename+transfer. Save 2–5 min.
- **Sizes match** → compute remote SHA-256 to distinguish same-content (skip) from
  hash collision (transfer). Same cost as today.
- **File missing** → no stat, no SHA-256, straight to transfer. Already fast.

For the common case where the remote file doesn't exist yet, this is free. For the
case where the remote file exists with matching content (skip), this halves the SSH
round-trips. For the rename case (different content, different size — most common for
truly different files), the full SHA-256 is avoided entirely.

### Post-transfer verification

The post-transfer `sha256sum` cannot easily be replaced with `stat` (we need to
verify the bits, not just the size). However, rsync already verifies data integrity
during transfer using its own checksum protocol. The SSH `sha256sum` adds a second
independent verification layer. Whether this is worth 2–5 minutes per file for large
files is a policy decision.

Options:
- Keep as-is (maximum integrity, slowest).
- Make post-transfer verification opt-in via `--verify` flag (default off).
- Replace with a `stat`-based size check post-transfer (fast but weaker).

### When to implement

Separately, after the timeout work is shipped. Start with the pre-transfer stat
optimization since it is unambiguously correct and has no integrity trade-off.
