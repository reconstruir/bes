# Cross-Platform Abstract Interface Framework (Python 3.13+)

## Core Concept

A filesystem-driven plugin architecture where the directory tree *is* the dispatch table. Python 3.13's improved type system and `importlib` machinery make this cleaner than ever.

---

## Directory Structure

```
myframework/
├── hooks/
│   └── hook-myframework.platforms.py   # collect_submodules, ships with package
├── _pyinstaller.py                      # get_hook_dirs() entry point target
├── interfaces/
│   └── package_manager.py              # Abstract base (Protocol + ABC hybrid)
├── platforms/
│   ├── __init__.py                      # empty, makes tree collectable
│   ├── _base.py                         # Universal fallback implementation
│   ├── linux/
│   │   ├── __init__.py                  # empty
│   │   ├── _base.py                     # Linux-generic fallback
│   │   ├── ubuntu/
│   │   │   ├── __init__.py
│   │   │   ├── _base.py                 # Ubuntu-generic (any version)
│   │   │   ├── v22.py                   # Ubuntu 22.x
│   │   │   └── v24.py                   # Ubuntu 24.x
│   │   ├── fedora/
│   │   │   ├── __init__.py
│   │   │   ├── _base.py
│   │   │   └── v40.py
│   │   └── arch/
│   │       ├── __init__.py
│   │       └── _base.py                 # Rolling; version rarely meaningful
│   ├── macos/
│   │   ├── __init__.py
│   │   ├── _base.py                     # macOS-generic fallback
│   │   ├── v13.py                       # Ventura
│   │   ├── v14.py                       # Sonoma
│   │   └── v15.py                       # Sequoia
│   └── windows/
│       ├── __init__.py
│       ├── _base.py                     # Windows-generic fallback + manager probe
│       ├── winget.py
│       ├── chocolatey.py
│       ├── scoop.py
│       └── msix.py                      # Direct MSIX/Store
└── resolver.py                          # Platform detection → module path → import
```

The resolution walk is: **most-specific → least-specific → universal**. If
`platforms/linux/ubuntu/v24.py` exists, use it. If not, try
`platforms/linux/ubuntu/_base.py`, then `platforms/linux/_base.py`, then
`platforms/_base.py`.

---

## Resolution Strategy

**Detection order** (all via stdlib — `platform`, `os`, `sys`):

1. OS family (`linux`, `macos`, `windows`)
2. macOS: major version integer from `platform.mac_ver()`
3. Linux: distro ID + major version via `/etc/os-release` (no `distro` third-party
   lib needed in 3.13 — though `distro` remains the robust choice for edge cases)
4. Windows: see Windows section below

The fallback chain is computed once at startup and cached. Each level in the chain
is a candidate dotted module path. First existing module wins.

**No `__init__` routing logic.** `resolver.py` uses `importlib.util.find_spec` with
dotted module names to check existence, then `importlib.import_module` to load.
`find_spec` works correctly in PyInstaller frozen bundles. The `__init__.py` files
in each subdirectory are empty (docstring only) — present solely to make the tree a
proper package hierarchy that PyInstaller's `collect_submodules` will pick up.

---

## Interface Layer

Defined with `typing.Protocol` (structural) plus an `ABC` base for enforcement —
the 3.13 way to get both duck-typing compatibility and explicit abstract method
errors. Methods are typed with the new `type` keyword aliases. Implementations must
satisfy the Protocol whether or not they inherit from it, but the ABC base is offered
as a convenience with helpful `NotImplementedError` messages pointing to the fallback
chain.

---

## macOS Specifics

- Major version only is sufficient (`v13`/`v14`/`v15`) — minor versions rarely
  warrant separate implementations
- The `_base.py` covers Homebrew which works across all modern macOS versions
- Version-specific files handle things like API availability, SIP behavior changes,
  or framework path shifts
- Resolution is clean and predictable: `macos/v15.py` → `macos/_base.py`

---

## Linux Specifics

- `/etc/os-release` is the canonical source — `ID` (distro slug) + `VERSION_ID`
  (often `"22.04"` or `"40"`) — take only the major component
- `ID_LIKE` field is valuable: Ubuntu has `ID_LIKE=debian`, enabling a deeper
  fallback chain: `ubuntu/v24` → `ubuntu/_base` → `debian/_base` → `linux/_base`
- Rolling distros (Arch, Void) typically only need `_base.py`
- The `ID_LIKE` chain depth is an open design question — see issues below

---

## Windows: The Hard Part

Windows has no canonical package manager. The resolution model changes: instead of
detecting the OS version and finding an implementation, you must **detect which
managers are available** and apply a preference order or policy.

**Available managers to consider:**

- **WinGet** — Microsoft's official tool, present on Win 11 and updated Win 10;
  most likely to be present but still not universal
- **Chocolatey** — longest-lived, broad package coverage, widely used in
  enterprise/dev environments
- **Scoop** — user-space only, no elevation required, dev-tool focused
- **MSIX/winget source** — underlying store mechanism
- **Conda/mamba** — relevant in data/science contexts
- **Manual/none** — always a real possibility

**Detection approach:** probe each manager's executable at startup via
`shutil.which`, build a priority list, cache it. The `windows/_base.py` owns this
probe logic and selects from the named implementation modules. Users/callers can also
inject preference via config or environment variable.

**Other Windows quirks:**

- Elevation/UAC for system-wide installs — the framework needs a concept of
  "requires elevation" that is only meaningful on Windows
- PowerShell vs CMD execution context matters for some manager operations
- Path separator and executable extension (`.exe`, `.cmd`) differences are handled
  by `shutil.which` but worth explicit documentation
- WSL: `/etc/os-release` will identify as Linux — this is correct behavior, but
  deserves an explicit note that WSL is treated as Linux, not Windows

---

## PyInstaller: Zero-Configuration Bundling

### The Problem

PyInstaller's hook system works by tracing imports statically. Dynamic imports via
`importlib` from computed paths are opaque to it. Everything under `platforms/`
would be silently excluded from a frozen bundle unless explicitly listed — exactly
the configuration burden this framework should avoid.

### The Solution

**Ship a hook file as part of the package.** PyInstaller 4.0+ discovers hooks
automatically via the `pyinstaller40` entry point group.

`hook-myframework.platforms.py` (ships in the `hooks/` directory):

```python
from PyInstaller.utils.hooks import collect_submodules
hiddenimports = collect_submodules('myframework.platforms')
```

`_pyinstaller.py` (the entry point target):

```python
from pathlib import Path

def get_hook_dirs():
    return [str(Path(__file__).parent / "hooks")]
```

`pyproject.toml` registration:

```toml
[project.entry-points."pyinstaller40"]
hook-dirs = "myframework._pyinstaller:get_hook_dirs"
```

The user runs `pyinstaller` and everything under `platforms/` is included with zero
configuration. This is the canonical pattern used by `pandas`, `scipy`, and
`cryptography`.

### Why the Empty `__init__.py` Files Are Required

`collect_submodules` only traverses real Python packages — directories with
`__init__.py`. Without them the hook cannot enumerate submodules and PyInstaller
cannot collect them. The files are genuinely empty (a docstring is sufficient); all
routing logic stays in `resolver.py`. This is the minimal `__init__` footprint
necessary for correct PyInstaller behavior and the community-standard approach.

### Resolver Import Mechanism

Because the `platforms/` tree is a proper package hierarchy, the resolver uses
**dotted module names** rather than filesystem paths:

```
myframework.platforms.linux.ubuntu.v24   # dotted — PyInstaller-visible
vs.
/path/to/platforms/linux/ubuntu/v24.py   # filesystem path — invisible to PyInstaller
```

Existence checks use `importlib.util.find_spec(dotted_name)` (works in frozen
bundles). Actual loading uses `importlib.import_module(dotted_name)`.

---

## Open Issues & Concerns

### Design Questions

1. **`ID_LIKE` chain depth on Linux** — how deep to follow? Ubuntu → Debian is
   obvious. Mint → Ubuntu → Debian gets unwieldy. Needs a cap or explicit opt-in
   per distro.

2. **Windows manager preference policy** — who decides the order? Hardcoded default
   (WinGet > Choco > Scoop), user config, or caller-injected? The framework probably
   needs to support all three with a clear override mechanism.

3. **Partial specialization** — what if `ubuntu/v24.py` only overrides one method?
   Mixin/delegation pattern needed, or just "inherit from `ubuntu/_base.py`"? The
   latter is simpler but means version files have an `import` dependency on their
   parent `_base`, which is reasonable but should be documented as the pattern.

4. **Discovery at import time vs. lazy** — computing the fallback chain once at
   startup is clean, but some environments (containers, CI) may mutate available
   tools after startup. Probably a non-issue for most uses; worth an explicit
   note in the docs.

5. **Version granularity contract** — "we specialize to major version only" should
   be explicit so contributors don't create `ubuntu/v22_04_3.py`. Enforced by
   convention and documented in `CONTRIBUTING`.

### Runtime Concerns

6. **Distro detection reliability** — `/etc/os-release` is nearly universal on
   modern Linux but not guaranteed on minimal/embedded/container images. When
   missing: treat as generic Linux (`platforms/linux/_base.py`).

7. **macOS SIP and sandboxing** — some operations behave differently under SIP.
   Version-specific files can encode this, but the interface may need a capability
   flag mechanism to surface constraints to callers.

8. **Windows without any manager** — the framework must have a graceful degradation
   story (raise a typed `NoPackageManagerError`, not an untyped crash) when nothing
   is detected.

9. **Testing matrix** — the combination of platforms × versions × managers is large.
   The recommended approach is mock platform detection (inject a fake `platform_info`
   at resolver construction time) rather than requiring real installs. CI matrix
   should test at least: Linux generic, Ubuntu 22/24, macOS generic, Windows with
   WinGet mocked, Windows with no manager.

10. **ARM vs x86 on macOS/Windows** — architecture can affect package availability
    and manager behavior (especially Rosetta 2 scenarios on macOS). Not currently
    represented in the filesystem hierarchy; may need a second resolution dimension
    or a capability flag if it becomes relevant.

11. **`find_spec` in frozen bundles** — `importlib.util.find_spec` is documented to
    work in PyInstaller frozen apps for collected submodules, but the fallback chain
    logic should have an integration test that runs against a minimal frozen binary
    in CI to catch regressions.

12. **Numeric/versioned module names** — dotted import of
    `myframework.platforms.linux.ubuntu.v24` is valid Python; the `v` prefix
    sidesteps linter complaints about numeric module names. This prefix convention
    must be documented and enforced in `CONTRIBUTING` so all version files follow it.


