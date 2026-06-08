# VFS Module — Analysis & Proposal

## What it is

The `vfs` module is a pluggable virtual filesystem abstraction layer.  It
defines a uniform interface (`vfs_base`) that different storage backends
implement, so callers can upload, download, list, remove files, and read/write
arbitrary key-value attributes against any configured backend without caring
whether the storage is a local directory, a git repo, or something else.

Two backends exist today:

| Backend | How it works |
|---|---|
| `vfs_local` | Wraps a local directory. Uses a SQLite DB (`.bes_vfs/metadata.db`) for attributes and a separate cache DB for SHA256 checksums. |
| `vfs_git_repo` | Clones a remote git repo, delegates all FS ops to a `vfs_local` proxy over the clone root, then auto-commits and pushes every mutation. |

The factory (`vfs_registry`) reads an INI-style config file (`~/.bes_vfs/config/*.bes_vfs`), resolves the backend class by name via a metaclass auto-registration scheme, validates fields, and instantiates the backend.  A CLI (`vfs_cli`) exposes all operations as subcommands.

---

## Current state

The module is a solid early-stage prototype with a clear architectural vision.
The abstractions are mostly in the right places.  However it has a mix of
unfinished work, copy-paste bugs, and several fundamental design problems
around attributes that will hurt when adding more backends.

---

## Bugs

### `vfs_git_repo.py`

| Location | Problem |
|---|---|
| Line 123 | `print('good')` left in production code |
| Line 124 | `#proxy.repo.push()` is commented out — uploads are never pushed |
| Line 119 | `bf_filename.extension()` called but `bf_filename` is never imported |
| Line 188 | `mkdir` error message says `vfs_artifactory` — wrong name, copied from elsewhere |
| Every read op | `_post_operation` (which runs `git status`) is called after `list_dir`, `has_file`, `file_info`, `download_*` — pointless overhead on reads; status only matters after writes |
| `_make_proxy()` | Creates a new clone-manager update on every single call — expensive if called in a tight loop |

### `vfs_cli_command.py`

| Location | Problem |
|---|---|
| Line 148 | `ow.getcwd()` — typo, should be `os.getcwd()` (NameError at runtime) |
| Line 170 | `fs.file_info(remote_filename)` — missing required `options` argument |
| Lines 68–69 | `print(x, type(x))` debug print left in `lsdir()` |
| Lines 88–91 | `show_attributes` formatting is commented out in `_format_file_info` |

### `vfs_local.py`

| Location | Problem |
|---|---|
| Line 145 | `_should_include_file` is declared as a regular method with `clazz` as first arg but has no `@classmethod` decorator — works by accident because `self` is named `clazz` |
| `_make_entry` | Opens a new `file_metadata` DB connection on every single file during a listing — O(n) DB opens per `list_dir` call |
| `.bes_vfs` DB keys | The SQLite DB stores **absolute local paths** as keys. Moving the root dir or cloning to a different machine silently breaks all attributes |

### `vfs_registry.py`

| Location | Problem |
|---|---|
| Lines 14–15 | The imports that would trigger metaclass auto-registration (`vfs_local`, `vfs_git_repo`) are commented out. The registry only works if something else imports those modules first — fragile implicit dependency |
| `vfs_class_path` loader | Loads custom classes by writing a temp `.py` file and `execfile`-ing it — fragile, leaves temp files, unnecessary |

### `vfs_tester.py`

| Location | Problem |
|---|---|
| `_call_fs` | Builds a `vfs_list_options` object but never passes it to the wrapped call (just calls `func(*args)`) — `OPTIONS` (the `vfs_file_info_options` with hardcoded mtime) is defined as a class var but never injected either, so tests always get real mtimes |

---

## Interface issues

### 1. No capability declaration

Every method in `vfs_base` is `@abstractmethod` — all backends must implement
everything.  There is no way to ask a backend "do you support attributes?",
"do you support `mkdir`?", "do you support recursive listing?".  You find out
by getting an exception (`mkdir` raises `vfs_error` in `vfs_git_repo`).

This is the root cause of the attributes problem (below) and will keep biting
with every new backend added.

### 2. `set_file_attributes` in the interface, `get_file_attributes` not

The base class requires all backends to implement `set_file_attributes`, but
reading attributes is only possible via `file_info()`, which fetches everything
— path, type, size, checksums, AND attributes — even when you only want the
attributes.  There is no lightweight `get_file_attributes(path, keys)` call in
the interface.

### 3. `options` plumbing is inconsistent

`list_dir(remote_dir, recursive, options)` and `file_info(remote_filename, options)` take an options object.  `has_file`, `remove_file`, `upload_file`, `download_*`, `set_file_attributes`, and `mkdir` do not.  The options object (`vfs_file_info_options`) currently only carries `hardcode_modification_date` for testing, which shouldn't be in the production interface at all.

### 4. `vfs_path` exists but is unused by the interface

`vfs_path.py` defines a proper path object with `abs_path`, `rel_path`, `parts`, `basename`, `dirname`.  The entire rest of the codebase ignores it — every method takes raw strings and normalizes them internally.  The path abstraction never materialized.

### 5. `list_dir` returns a flat `vfs_file_info_list`, not a tree

When `recursive=True`, `list_dir` returns a tree embedded in the `children`
field of each dir entry.  When `recursive=False` it returns a flat list of
top-level entries.  This asymmetry means callers have to handle two completely
different shapes depending on the flag.

---

## The attributes problem

This is the most structural issue in the design.

### How it works now

Attributes are stored in a SQLite database at
`<root>/.bes_vfs/metadata.db`, managed by the `file_metadata` class.  The
database stores `(section, filename, key, value)` rows where `filename` is the
**absolute local path** of the file.

```
table: attributes
key: /Users/ramiro/some/root/dir/foo/bar.bin
values: version=1.2 platform=linux
```

This means attributes are:
- Only supported by `vfs_local` (and transitively `vfs_git_repo` because it
  wraps a local clone)
- Keyed on absolute local paths, so they silently disappear if the root dir
  changes or the repo is cloned elsewhere
- Committed into the git repo as a binary SQLite file in `.bes_vfs/` — not
  human-readable, not diffable, causes constant `.bes_vfs` churn commits
- Forbidden on directories (hardcoded `raise vfs_error` in `vfs_file_info.__new__`)
- Tightly coupled to the FS — you can't have attributes without having the
  `.bes_vfs` sidecar

### Why it breaks for real remote backends

Consider S3, SFTP, WebDAV, or Azure Blob:

| Backend | Native attribute support |
|---|---|
| S3 / compatible | User-defined object metadata (`x-amz-meta-*` headers), limited to 2KB per object. No native support on "directories" (prefixes). |
| Azure Blob | Metadata dict per blob. Directories don't really exist. |
| Google Cloud Storage | Custom metadata per object. |
| WebDAV | `PROPFIND`/`PROPPATCH` — real first-class property support. |
| SFTP | No native key-value metadata. Would need a sidecar. |
| SMB / NFS | Extended attributes (`xattr`) — OS-level, availability varies. |
| Plain HTTP | Read-only. Response headers only. No writable attributes. |
| Local filesystem | `xattr` on macOS/Linux — OS-native but not universally available (no-op on FAT, some network mounts). |

The current design assumes attributes are always available and always writable.
It silently stores them in a local SQLite DB regardless of the backend — so a
caller using `vfs_git_repo` thinks they're storing attributes "in the repo",
but they're actually in a SQLite file that is committed separately and breaks
on re-clone.

---

## Proposal: better abstraction

### 1. Capability flags

Add a `capabilities()` classmethod to `vfs_base` that returns a frozenset.
Callers check capabilities before attempting unsupported operations.  Backends
that don't support a feature raise `vfs_capability_error` (a distinct subclass
of `vfs_error`) so callers can catch and handle it cleanly.

```python
class vfs_capability:
  ATTRIBUTES        = 'attributes'          # read/write file attributes
  DIR_ATTRIBUTES    = 'dir_attributes'      # attributes on directories
  MKDIR             = 'mkdir'               # create directories
  RECURSIVE_LIST    = 'recursive_list'      # server-side recursive listing
  CHECKSUMS         = 'checksums'           # content checksums provided natively
  STREAMING         = 'streaming'           # stream-based transfer (not just bytes)
  ASYNC             = 'async'               # async-native implementation

class vfs_base:
  @classmethod
  def capabilities(clazz) -> frozenset[str]:
    return frozenset()
```

### 2. Decouple attribute storage from the FS backend

Introduce a separate `vfs_attr_backend` interface:

```python
class vfs_attr_backend(ABC):
  @abstractmethod
  def get(self, remote_path: str, keys: list[str] | None) -> dict[str, str]: ...

  @abstractmethod
  def set(self, remote_path: str, attributes: dict[str, str]) -> None: ...

  @abstractmethod
  def delete(self, remote_path: str, keys: list[str]) -> None: ...
```

Concrete implementations:
- `vfs_attr_backend_sqlite` — current behavior, SQLite sidecar (but keyed on
  normalized VFS paths, not absolute local paths)
- `vfs_attr_backend_yaml` — human-readable YAML sidecar file per directory
  (easy to diff in git, easy to hand-edit)
- `vfs_attr_backend_native` — delegates to the backend's own metadata
  (S3 object metadata, GCS custom metadata, WebDAV properties)
- `vfs_attr_backend_xattr` — OS-level extended attributes for local FS

The VFS factory can wire up a `vfs_attr_backend` independently of the FS
backend.  A `vfs_git_repo` could use `vfs_attr_backend_yaml` so attributes are
stored as readable YAML committed alongside files, not a binary SQLite blob.

### 3. Add `get_file_attributes` to the interface

```python
@abstractmethod
def get_file_attributes(self, remote_filename: str, keys: list[str] | None = None) -> dict[str, str]:
    'Return attributes for remote_filename. If keys is None, return all.'
    pass
```

This avoids fetching checksums, size, and mtime just to read a couple of keys.

### 4. Separate `vfs_file_info` from attribute data

`vfs_file_info` currently embeds `attributes: dict | None`.  For backends that
don't support attributes, this is always `None`.  For backends that do, fetching
attributes on a directory listing is often expensive (one API call per file).

Split into two types:

```python
@dataclass(frozen=True)
class vfs_file_info:
  filename: str
  ftype: str                          # 'file' | 'dir'
  modification_date: datetime
  size: int | None
  checksums: checksum_set | None

@dataclass(frozen=True)  
class vfs_file_info_with_attrs(vfs_file_info):
  attributes: dict[str, str]
```

Or alternatively, make `list_dir` accept an `include_attributes: bool` flag so
callers opt in to the expensive per-file attribute fetches.

### 5. Fix the path key problem

Change `vfs_attr_backend_sqlite` (and any sidecar) to key on the **normalized
VFS path** relative to the root, not the absolute local path.  This makes the
DB portable across machines, clones, and root dir changes.

```python
# current (broken)
db.replace_values('attributes', local_filename, ...)  # /Users/ramiro/root/foo.bin

# proposed
db.replace_values('attributes', remote_filename, ...)  # foo.bin
```

### 6. Remove `hardcode_modification_date` from `vfs_file_info_options`

This is test scaffolding living in the production interface.  Move it into
`vfs_tester` which should monkey-patch modification dates at the tester level,
not by contaminating the options passed to real implementations.

---

## Proposed new backends (2026)

### S3-compatible object storage

The most important missing backend.  Covers AWS S3, MinIO, Backblaze B2,
Wasabi, Cloudflare R2.  Use `boto3` or `s3transfer`.

```
capabilities: ATTRIBUTES (via x-amz-meta-*), CHECKSUMS (ETag/MD5),
              no MKDIR (prefixes only), RECURSIVE_LIST (via list_objects_v2)
```

Attribute notes: S3 user metadata is immutable per object — updating a
single attribute requires a server-side copy (`copy_object` with new
metadata).  Keys must be ASCII, total metadata ≤ 2 KB.  These constraints
should be surfaced via capability flags, not hidden behind the abstraction.

### WebDAV

Covers Nextcloud, ownCloud, SharePoint (OneDrive for Business), Apache WebDAV.
Use `webdavclient3` or `aiohttp`.

```
capabilities: ATTRIBUTES (PROPFIND/PROPPATCH), DIR_ATTRIBUTES, MKDIR,
              RECURSIVE_LIST (with Depth: infinity header — not universal)
```

WebDAV is the one protocol that has genuinely first-class arbitrary metadata
via properties.  It maps cleanly to the VFS attribute model.

### SFTP / SSH

Covers any Unix host, NAS devices, Synology, TrueNAS.  Use `paramiko` or
`asyncssh`.

```
capabilities: MKDIR, no ATTRIBUTES natively (needs sidecar),
              no CHECKSUMS natively (would need remote md5sum subprocess)
```

Pair with `vfs_attr_backend_yaml` for attribute storage via a `.vfs_attrs/`
directory tree alongside files.

### Rclone as a universal shim

`rclone` already speaks 70+ backends (S3, GCS, Azure, Dropbox, Google Drive,
OneDrive, SFTP, WebDAV, local, etc.) and normalizes them.  A `vfs_rclone`
backend that shells out to `rclone` (or uses `rclone serve webdav` as a local
proxy) gives instant coverage of everything rclone supports, without writing
provider-specific code.

```
capabilities: MKDIR, RECURSIVE_LIST, no ATTRIBUTES (rclone metadata support
              is partial and backend-specific)
```

Good for "good enough" coverage; native backends are better for performance and
attribute support.

### Google Drive / Dropbox / OneDrive

Consumer cloud storage.  Attributes can use the native "custom properties"
API each provides (all three have this).  No real directory hierarchy — all
are flat ID-based stores with path illusions.

### Azure Blob Storage

Use `azure-storage-blob`.  Very similar to S3.  Metadata has the same
copy-to-update limitation.  Blob tags (a separate system from metadata) are
queryable — could be used as a richer attribute backend.

### Local with xattr

Replace the SQLite sidecar for `vfs_local` with OS-level extended attributes
(`xattr` module on macOS/Linux).  Attributes live on the inode itself —
no sidecar file, no path key problem, works with any tool that reads xattrs.
Caveat: not supported on FAT, exFAT, some network mounts.  Detect at runtime
and fall back to the SQLite backend.

### Async-native interface

All network backends are fundamentally async.  A blocking API built on
`threading` or `concurrent.futures` works but wastes resources under load.
For 2026 consider adding an async mirror of the interface:

```python
class vfs_async_base(ABC):
  @abstractmethod
  async def list_dir(self, remote_dir, recursive, options): ...
  @abstractmethod
  async def upload_file(self, local_filename, remote_filename): ...
  # etc.
```

Sync implementations wrap the async ones with `asyncio.run()`.  Async-native
backends (aiohttp, asyncssh, aiobotocore) implement only the async interface.

---

## Summary of recommended actions (ordered by impact)

1. **Fix the bugs** — the commented-out push, the `bf_filename` missing import,
   `ow.getcwd()`, and the `print('good')` are blockers for `vfs_git_repo` even
   working correctly today.

2. **Key attributes on VFS paths, not absolute local paths** — one-line fix in
   `set_file_attributes` / `_make_entry` in `vfs_local`, but it changes the DB
   schema so do it before any data is in production.

3. **Add capability flags** — low-effort, high payoff.  Lets you add S3 or
   SFTP without pretending they support everything.

4. **Extract `vfs_attr_backend`** — medium effort.  Needed before adding any
   backend that has different attribute semantics than "SQLite sidecar".

5. **Re-import the concrete classes in `vfs_registry`** — uncomment the two
   import lines so auto-registration actually fires reliably.

6. **`vfs_git_repo` attribute flow** — swap from SQLite to
   `vfs_attr_backend_yaml` so attributes are human-readable, diffable, and not
   broken by re-clone.

7. **Add S3-compatible backend** — first real remote backend, proves the
   capability + attribute abstraction works.

---

## `vfs_rclone` in detail

`rclone` is a CLI tool that already knows how to talk to 70+ storage backends
and presents them all through a uniform command set (`rclone ls`, `rclone copy`,
`rclone delete`, `rclone cat`, ...).

Instead of writing a `vfs_s3`, `vfs_sftp`, `vfs_dropbox`, etc., you write one
`vfs_rclone` backend that shells out to rclone commands.  The user configures
rclone normally (`~/.config/rclone/rclone.conf`) with a named remote like
`mynas:` or `mys3bucket:`, and the VFS config just says `vfs_type = rclone` +
`remote = mynas:files`.  Your code never needs to know it's SFTP vs S3 vs
anything else — rclone handles all of that.

### Option A — shell out directly

Every VFS method maps to a `subprocess` call:

```python
def download_to_file(self, remote_filename, local_filename):
    subprocess.run(['rclone', 'copyto', f'{self._remote}/{remote_filename}', local_filename], check=True)

def upload_file(self, local_filename, remote_filename):
    subprocess.run(['rclone', 'copyto', local_filename, f'{self._remote}/{remote_filename}'], check=True)

def list_dir(self, remote_dir, recursive, options):
    flags = ['--recursive'] if recursive else ['--max-depth', '1']
    out = subprocess.check_output(['rclone', 'lsjson', f'{self._remote}/{remote_dir}'] + flags)
    entries = json.loads(out)
    # parse into vfs_file_info_list ...
```

`rclone lsjson` returns JSON with name, size, mtime, IsDir — maps directly to
`vfs_file_info`.  Simple, works everywhere rclone works.

### Option B — `rclone serve webdav`

Spin up a local WebDAV server pointed at the remote:

```bash
rclone serve webdav mynas:files --addr localhost:8080
```

Then `vfs_rclone` is just `vfs_webdav` pointed at `localhost:8080`.  You get
full WebDAV semantics including real properties (`PROPFIND`) for attributes.
The subprocess management is slightly more involved (start on init, stop on
teardown) but the VFS layer itself becomes trivially thin.

### The attributes catch

`rclone lsjson` gives name, size, mtime, IsDir — no metadata/attributes.
`set_file_attributes` has no rclone equivalent.  So `vfs_rclone` has
`ATTRIBUTES` absent from its capabilities and pairs with an external
`vfs_attr_backend` (SQLite or YAML sidecar) when attributes are needed.
This is exactly why the capability + separate attr backend proposal is the
right foundation — `vfs_rclone` becomes a first-class citizen without faking
attribute support.

### The meta-backend composition bonus

rclone backends stack.  You can layer `crypt` on top of `union` on top of two
S3 buckets and rclone presents it as one encrypted remote.  `vfs_rclone` gets
all of that for free — encryption, deduplication, sharding across providers —
without your code knowing any of it is happening.

---

## rclone backend catalog

Roughly 70+ backends grouped by category.

### S3-compatible object storage

One rclone provider, many targets: AWS S3, Cloudflare R2, Backblaze B2, Wasabi,
MinIO, DigitalOcean Spaces, Scaleway, Linode Object Storage, IDrive e2, IONOS,
Alibaba OSS, Tencent COS, Huawei OBS, IBM COS, Qiniu KODO, SeaweedFS, Storj
(S3 mode), Synology C2, and ~15 more S3-compatible hosts.

### Big cloud

Google Cloud Storage, Azure Blob Storage, Azure Files.

### Consumer cloud drives

Google Drive, OneDrive, SharePoint, Dropbox, Box, pCloud, MEGA, Jottacloud,
Yandex Disk, Zoho WorkDrive, Koofr, Proton Drive, Filen, Mail.ru Cloud,
Mediafire, Pikpak, Put.io, Premiumize.me.

### Protocol-based

SFTP, FTP, WebDAV, SMB/CIFS, HTTP (read-only).

### Meta / compositing backends

These are the interesting ones — they layer on top of any other remote:

| Backend | What it does |
|---|---|
| `crypt` | Transparent encryption layer over any other remote |
| `compress` | Transparent compression layer over any other remote |
| `chunker` | Splits files larger than a threshold across any backend |
| `cache` | Caching layer in front of any slow remote |
| `union` | Presents multiple remotes as a single merged filesystem |
| `combine` | Mounts multiple remotes at different paths under one root |
| `alias` | Rename/repath any remote |
| `memory` | Ephemeral in-memory filesystem (useful for testing) |

Because these compose, a single rclone remote name can represent something like
"encrypted, compressed, striped across two S3 buckets" — and `vfs_rclone` sees
none of that complexity.

### Local / near-local

Local filesystem, Storj (native), IPFS (via MFS).
