# uv project and uv installer — design plan

## Goal

Create two new modules:

- **`lib/bes/uv/`** — programmatic management of uv-backed virtual
  environments, in the spirit of `pip_project` but designed from scratch for
  uv's model
- **`lib/bes/uv_installer/`** — bootstrapping uv itself on macOS, Linux, and
  Windows, in the spirit of `python_installer` but for a single binary tool

No pip_project code is reused.  These are new modules that happen to sit
alongside the old ones.

---

## What's wrong with pip_project (don't repeat this)

Understanding the pain points is essential to not carrying them forward.

1. **Options not `bcli_options`.**  `pip_installer_options` uses the old
   ad-hoc `__init__(**kargs) / setattr` pattern with a `blurber` field.
   New modules use `bcli_options` throughout.

2. **Downloading in `__init__`.**  `python_virtual_env._install_pip()` fetches
   `get-pip.py` from the internet synchronously during construction.  There is
   no offline mode and no way to supply a cached copy.  This is the worst kind
   of side-effect in a constructor.

3. **Bootstrapping tangled into the venv layer.**  `python_virtual_env`
   handles both venv creation and pip installation.  Those are two separate
   concerns.

4. **Silent opinionated defaults.**  `_ensure_basic_packages` installs
   `wheel` and `setuptools` unconditionally.  The caller never asked for this.

5. **Linux-specific hack in core code.**  `_reinstall_pip_if_needed` exists
   because "on linux there are problem with old python versions".  This is a
   workaround baked into the core class with no escape hatch.

6. **Fake HOME and TMPDIR.**  `pip_project` creates `.droppings/fake-home` and
   `.droppings/fake-tmp` to isolate side effects.  This is a defensive hack
   that exists because pip is poorly behaved.  uv does not have this problem.

7. **`_cleanup_tmpdir` doesn't clean.**  The method is called after every pip
   command but only prints filenames; it does not actually remove anything.

8. **Duplicate property definition.**  `pip_project_config` defines
   `python_exe` twice (lines 27 and 30).  The second silently shadows the
   first.  The config class is barely used.

9. **`call_program` env merging is fragile.**  It deep-copies kwargs, pulls
   PATH/PYTHONPATH out of a nested dict, merges manually, then re-inserts.
   This pattern is hard to follow and easy to break.

10. **`blurber` coupling.**  Options objects carry a `blurber` instance.
    Any code path that wants progress output must access it through options.
    This is the source of the `AttributeError: Unknown option: "blurber"`
    class of bugs.

---

## Module layout

```
lib/bes/uv/
  uv_error.py
  uv_exe.py                  # find/verify the uv binary
  uv_exe_info.py             # version, path, platform capabilities
  uv_venv.py                 # low-level: create/verify a venv via uv
  uv_project.py              # high-level: install, run programs in a venv
  uv_project_options.py
  uv_project_command_factory.py
  uv_project_command_handler.py
  uv_project_command_options.py

lib/bes/uv_installer/
  uv_installer_error.py
  uv_installer_options.py
  uv_installer_base.py
  uv_installer_macos.py
  uv_installer_linux.py
  uv_installer_windows.py
  uv_installer.py            # dispatcher (mirrors python_installer pattern)
  uv_installer_command_factory.py
  uv_installer_command_handler.py
  uv_installer_command_options.py
```

---

## `lib/bes/uv_installer/`

### Purpose

Bootstrap uv itself from nothing.  After this runs, a `uv` binary is present
at a known path.

### Platform strategies

| Platform | Primary | Alternative |
|---|---|---|
| macOS | `curl … astral.sh/uv/install.sh \| sh` | `brew install uv` |
| Linux | `curl … astral.sh/uv/install.sh \| sh` | distro package manager (optional) |
| Windows | `powershell -c "irm astral.sh/uv/install.ps1 \| iex"` | `winget install astral-sh.uv` |

### `uv_installer_base`

Abstract base class (use `metaclass=ABCMeta`, not `with_metaclass`).

```
abstractmethods:
  install(version=None)       # None means "latest"
  uninstall()
  is_installed() -> bool
  installed_version() -> str | None
  exe_path() -> str | None    # absolute path to the uv binary after install
```

### `uv_installer_options`

`bcli_options` subclass.

```
fields:
  install_dir   str   default=None    # override default install location
  version       str   default=None    # pin a specific version, None=latest
  verbose       bool  default=False
  dry_run       bool  default=False
```

`resolve_install_dir()` method: returns `~/.local/bin` on Unix,
`%USERPROFILE%\.local\bin` on Windows, unless overridden.

### `uv_installer` dispatcher

Same pattern as `python_installer`: holds a `_INSTALLER_CLASSES` dict keyed
by `host.MACOS / host.LINUX / host.WINDOWS`, instantiates the right one, and
delegates all calls.  Provides a `available_installers(system)` classmethod.

### Offline / cached install

Both the shell script and the PowerShell script can be downloaded separately
and supplied as a local file path.  `uv_installer_options` should support
`install_script` (a local path) so that environments without outbound internet
can still install uv from a pre-fetched script.

### Version pinning

When `options.version` is set, pass `UV_VERSION=<version>` in the environment
before running the install script.  The astral.sh scripts honour this variable.
For winget, use `--version`.

### After install

Call `uv_exe.find()` to confirm the binary is visible.  If it is in
`~/.local/bin` and that is not on PATH, emit a clear warning rather than
silently succeeding.

---

## `lib/bes/uv/`

### `uv_exe`

Locates the `uv` binary.  Resolution order:

1. `options.uv_exe` if explicitly set
2. `UV` environment variable
3. `~/.local/bin/uv` (Unix) / `%USERPROFILE%\.local\bin\uv.exe` (Windows)
4. `shutil.which('uv')`

Raises `uv_error` if not found rather than returning None silently.

`uv_exe.version(exe)` → parses `uv --version` output into a version tuple.

### `uv_venv`

Low-level venv management.  All it knows is a root directory and a uv binary.

```
uv_venv(root_dir, uv_exe, python=None)
  create()      # runs: uv venv [--python <ver>] <root_dir>
                # idempotent: skips if .venv/pyvenv.cfg already present
  python_exe    # cached_property: path to the python inside the venv
  bin_dir       # cached_property
  site_packages_dir  # cached_property
  is_valid()    # checks pyvenv.cfg exists and python_exe is executable
```

No package installation.  No environment construction.  No side effects beyond
running `uv venv`.

**No download in `__init__`.**  `create()` is a separate explicit call.

### `uv_project`

High-level.  Owns a `uv_venv` and knows how to install packages and run
programs inside it.

```
uv_project(options: uv_project_options)
  ensure_ready()           # create venv if needed; no implicit install
  install(package, version=None)
  install_requirements(requirements_files)
  installed() -> list[installed_package(name, version)]
  outdated() -> list[outdated_package(name, current, latest)]
  upgrade(packages)
  needs_upgrade(package) -> bool
  version(package) -> str
  call_uv(args, ...)       # run uv with the venv activated
  call_program(args, ...)  # run any program inside the venv environment
  program_path(program)    # absolute path to a binary in the venv
  has_program(program) -> bool
  env                      # property: minimal env dict for subprocess calls
```

#### Key design differences from pip_project

**`ensure_ready()` instead of side effects in `__init__`.**  The constructor
does not create the venv, install packages, or touch the filesystem.  Callers
explicitly call `ensure_ready()` when they want the venv to exist.  This makes
the object safe to construct for introspection-only use cases.

**No fake HOME or TMPDIR.**  uv is well-behaved; it does not scatter files in
`$HOME`.  The env property sets only what is strictly necessary: `VIRTUAL_ENV`,
`PATH` (prepend the venv bin dir), and `PYTHONPATH` if non-empty.

**No opinionated bootstrap packages.**  `uv_project` does not secretly install
`wheel` or `setuptools`.  If the caller wants them, they call `install()`.

**Requirements checksum cache.**  Keep the pip_project pattern of storing a
checksum alongside each requirements file to skip reinstalls when the file has
not changed.  Store checksums in `.uv_cache/requirements_checksums/` inside
the venv root.

**`call_program` is simple.**  Clone the current environment, prepend the venv
`bin` dir to `PATH`, set `VIRTUAL_ENV`.  No PATH/PYTHONPATH extraction from
nested dicts.

**No blurber on options.**  Progress output uses the `blurb` global directly
if `options.verbose` is True.  Options carry `verbose: bool`, not a blurber
instance.

### `uv_project_options`

`bcli_options` subclass.

```
fields:
  uv_exe        str   default=None    # explicit path to uv binary
  python        str   default=None    # python version or exe path for uv venv
  root_dir      str   default=None
  verbose       bool  default=False
  debug         bool  default=False
```

`resolve_root_dir()`: returns `path.abspath(root_dir)` if set, otherwise
`cwd/UV_PROJECT_ROOT`.

`resolve_uv_exe()`: delegates to `uv_exe.find(options.uv_exe)`.

### `env` property

```python
@property
def env(self):
    env = os_env.make_clean_env()
    env_var(env, 'VIRTUAL_ENV').value = self._venv.root_dir
    env_var(env, 'PATH').prepend(self._venv.bin_dir)
    return env
```

If the caller needs extra env vars (e.g. credentials), they pass them to
`call_program` directly rather than mutating a global on the object.

---

## Calling uv commands

All uv subcommands are invoked as:

```
<uv_exe> <subcommand> [args]
```

with `VIRTUAL_ENV` set so that uv operates on the correct environment without
needing `--prefix` everywhere.

For package operations: `uv pip install`, `uv pip list --format json`,
`uv pip list --outdated --format json`, `uv pip uninstall`.

For environment creation: `uv venv [--python <spec>] <root_dir>`.

---

## What is NOT in scope

- uv's project-level lockfile features (`uv init`, `uv add`, `uv lock`,
  `uv sync`).  Those are a different abstraction — this module targets the
  simple "venv + packages" use case that pip_project serves.
- Python installation via uv (`uv python install`).  That is a separate
  concern and belongs in `python_installer` or a future `uv_python_installer`.
- Migrating pip_project callers.  The new module coexists; callers migrate
  separately.

---

## File-by-file summary

| File | Responsibility |
|---|---|
| `uv/uv_error.py` | Exception class |
| `uv/uv_exe.py` | Find and validate the uv binary |
| `uv/uv_exe_info.py` | Version and path info (namedtuple) |
| `uv/uv_venv.py` | Create/verify a venv; no package ops |
| `uv/uv_project.py` | Install packages, run programs |
| `uv/uv_project_options.py` | `bcli_options` for uv_project |
| `uv/uv_project_command_factory.py` | bcli factory for CLI commands |
| `uv/uv_project_command_handler.py` | Handlers for CLI commands |
| `uv/uv_project_command_options.py` | CLI-level options |
| `uv_installer/uv_installer_error.py` | Exception class |
| `uv_installer/uv_installer_options.py` | `bcli_options` for installer |
| `uv_installer/uv_installer_base.py` | ABC with install/uninstall interface |
| `uv_installer/uv_installer_macos.py` | curl script + brew strategies |
| `uv_installer/uv_installer_linux.py` | curl script strategy |
| `uv_installer/uv_installer_windows.py` | PowerShell script + winget strategies |
| `uv_installer/uv_installer.py` | Dispatcher (host → installer class) |
| `uv_installer/uv_installer_command_factory.py` | bcli factory |
| `uv_installer/uv_installer_command_handler.py` | Handlers |
| `uv_installer/uv_installer_command_options.py` | CLI-level options |
