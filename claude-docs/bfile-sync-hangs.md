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

Three layers, each catching what the previous misses.

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

### Layer 2 — SSH keepalive flags (connection-level)

SSH `ServerAliveInterval=N ServerAliveCountMax=M`: the SSH client sends a keepalive
probe to the server every N seconds; if M consecutive probes go unanswered, SSH exits.
Total silence budget = N × M seconds. This **catches the observed case** — the SSH
channel is open but the NAS is unresponsive.

Also add `ConnectTimeout=N`: caps how long SSH waits to establish the initial
connection.

Applied to every SSH command builder in `bf_rsync_file_sync`:

**rsync `-e ssh ...` string** — affects the SSH session rsync runs over:
```
ssh -i {key} -o ConnectTimeout=30 -o ServerAliveInterval=30 -o ServerAliveCountMax=3 ...
```

**All `bssh_command` calls** (`sha256sum`, `mkdir -p`, `cleanup`) — add to `ssh_args`:
```python
ssh_args += [
  '-o', 'ConnectTimeout=30',
  '-o', 'ServerAliveInterval=30',
  '-o', 'ServerAliveCountMax=3',
]
```

Total silence budget for SSH commands: 30 × 3 = **90 seconds**.

### Layer 3 — process-level timeout in `execute.execute`

Belt-and-suspenders: if layers 1 and 2 fail (e.g. rsync ignores `--timeout`, or
SSH ignores keepalives due to a kernel-level TCP stall), a wall-clock alarm kills
the subprocess.

Add an optional `timeout_seconds` parameter to `execute.execute`:

```python
try:
  output = process.communicate(input=input_data, timeout=timeout_seconds)
except subprocess.TimeoutExpired:
  process.kill()
  process.communicate()   # drain pipes after kill
  raise execute_timeout_error(f'command timed out after {timeout_seconds}s: {parsed_args}')
```

`execute_timeout_error` is a new subclass of the existing error type so callers can
catch it specifically.

For rsync, a fixed wall-clock timeout is wrong (a 100 GB file on a slow link could
legitimately take hours). Use `None` (no process-level timeout) for rsync — layers 1
and 2 are sufficient. For SSH-only commands (`sha256sum`, `mkdir`, `cleanup`) use a
fixed **120 seconds** — any of these taking longer than 2 minutes indicates a hang.

---

## Retry behaviour (already correct)

When any of the above timeouts fires, the exception propagates out of `_sync_one`,
gets caught by the `_run_loop` error handler, emits a `RETRY` line, sleeps
`retry_wait_seconds`, and retries the file. rsync `--partial` + `--partial-dir`
means the next attempt resumes from where the previous left off, which is exactly
what the user observed when they manually re-ran.

**No changes needed to retry logic.**

---

## Configuration

| Setting | Default | Expose as parameter? |
|---------|---------|---------------------|
| rsync `--timeout` | 300 s | No — hardcode is fine; rarely needs tuning |
| SSH `ConnectTimeout` | 30 s | No |
| SSH `ServerAliveInterval` | 30 s | No |
| SSH `ServerAliveCountMax` | 3 | No |
| SSH command process timeout | 120 s | No |

None of these need to be user-tunable for this use case. If they do later, they can
be added to `__init__` alongside `retry_wait_seconds`.

---

## Open issues

1. **SSH keepalive requires server support**: `ServerAliveInterval` is a client-side
   keepalive; TrueNAS (OpenSSH) supports it by default. No server-side config needed.

2. **rsync `--timeout` vs SSH keepalive interaction**: if `--timeout=300` fires
   first, rsync exits and the SSH channel closes normally. If the SSH keepalive
   fires first (90 s × layer-2 budget), SSH exits and rsync gets a broken pipe.
   Both produce a non-zero exit code; both are caught by the retry loop. No
   conflict.

3. **Process-level timeout for rsync**: A 100 GB file at 100 MB/s takes ~17 min.
   Any fixed timeout would be too short for large files or slow links. Do **not**
   add a process-level wall-clock timeout to rsync. Layers 1 and 2 are enough.

4. **`execute.execute` change scope**: Adding `timeout_seconds` to `execute.execute`
   is a small, additive change. `None` means no timeout (current behaviour), so
   all existing callers are unaffected. Only the `bssh_command` calls in
   `bf_rsync_file_sync` will pass a value.

---

## Implementation plan

1. Add `timeout_seconds=None` to `execute.execute`, using `communicate(timeout=N)`
   with SIGKILL fallback and a new `execute_timeout_error` exception class.

2. Add `timeout_seconds=None` to `system_command.call_command` and thread it
   through to `execute.execute`.

3. In `bf_rsync_file_sync`:
   - Add `--timeout=300` to the rsync args in `_rsync`.
   - Add SSH keepalive options to the `-e ssh ...` string in `_rsync`.
   - Extract a helper `_ssh_args()` that returns the base SSH args list (key,
     port, strict-host, known-hosts) so the keepalive options are added in one
     place and shared by `_ssh_sha256`, `_ssh_mkdir`, `_cleanup_partial`.
   - Pass `timeout_seconds=120` to `bssh_command.call_command` in all three
     SSH-only methods.
