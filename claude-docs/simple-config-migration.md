# simple_config Module — Audit and TOML Migration Proposal

## What the module does

`simple_config` is a custom configuration format built on `tree_text_parser` (an indentation-based parser). The on-disk format looks like this:

```
# Comment support
section
  key1: value1
  key2: value2
  key3: ${ENV_VALUE3}
  key4[sensitive]: ~/.foo/something.txt

basic
  color: red
  flavor: tart

fancy extends basic
  flavor: spicy
```

Each top-level identifier is a section. Keys are indented one level under their section. The format supports:

- **Section inheritance** (`fancy extends basic`) — the child section transparently inherits all keys from the parent, with its own values winning.
- **Environment variable interpolation** (`${VAR}`) — resolved at read time, with fallback to locally-set variables.
- **Key annotations** (`key[flag, attr=value]: ...`) — arbitrary metadata attached to individual entries; not resolved by the parser, only stored.
- **Multi-file hierarchical loading** (`simple_config_files`) — scans a search path for matching files, merges sections across files, and performs full dependency resolution on `extends` relationships.
- **Round-trip serialization** — `to_string()` / `save()` reproduce the original text including ordering.
- **Typed accessors** — `get_bool()`, `get_string_list()`, though all underlying storage is strings.
- **Key validation modes** — `attrib` (identifier-safe), `any`, `fnmatch` (glob patterns as keys).
- **Source origin tracking** — every entry and section records `(source_file, line_number)` for error messages.

---

## Audit

### What works well

- **Type checking via `check`** — consistent argument validation everywhere.
- **Origin tracking** — errors always cite file and line number.
- **`simple_config_files`** — hierarchical multi-file loading with topological sort for `extends` is genuinely useful and non-trivial.
- **Variable scoping** — section-level variables fall back to config-level variables, which fall back to `os.environ`.

### Bugs

**1. `__hasattr__` is not a Python protocol** (`simple_config.py:91`)

```python
def __hasattr__(self, section_name):
    return self.find(section_name) != None
```

Python does not call `__hasattr__`. `hasattr(obj, name)` is equivalent to `try: getattr(obj, name); return True; except AttributeError: return False`. This method is dead code and never called.

**2. `remove_section` drops `origin` from the error message** (`simple_config.py:117`)

```python
raise simple_config_error('no such section found: "{}"'.format(section_name, self._origin))
```

The format string has one `{}` placeholder but two arguments. `self._origin` is silently discarded. The error message never shows where the lookup failed.

**3. Wrong field name in `simple_config_files._make_maps()`** (`simple_config_files.py:99`)

```python
raise simple_config_error(msg, section.origin)   # wrong
# should be:
raise simple_config_error(msg, section.origin_)  # namedtuple field uses trailing underscore
```

**4. Typo in `_resolve_seach_path_part`** (`simple_config_files.py:56`)

"seach" should be "search". Private method, but still part of the codebase.

### Design issues

**5. Namedtuple with mutable state** (`simple_config_section`)

`simple_config_section` is a `namedtuple` but `entries_` is a plain `list` that gets mutated by `set_value()`, `add_value()`, `delete_value()`, and `clear_values()`. Namedtuples have value semantics and are expected to be immutable. Using one as a mutable container is misleading and makes it impossible to use the instance as a dict key or in a set.

`simple_config_section.__setattr__` routes to `set_value()` to paper over this, but that hook fires for all attribute assignments, including internal ones. This is fragile.

**6. Section auto-creation on access** (`simple_config.py:176–181`)

`__getattr__` routes through `find()` → `section()`, which calls `add_section()` if the name is not found:

```python
def section(self, section_name, matcher=None):
    if not self.has_unique_section(section_name, matcher=matcher):
        self.add_section(section_name)            # silently creates!
    ...
```

Accessing `config.typo_section` silently creates a new empty section instead of raising `AttributeError`. This hides typos completely.

**7. Misleading name `has_unique_section`** (`simple_config.py:119`)

The method returns `True` if *any* section with the name exists, not that there is *exactly one*. The name implies a uniqueness guarantee. Callers who want to distinguish "exists" from "exists exactly once" cannot use this.

**8. Duplicate constants** (`simple_config_options` and `simple_config_keys`)

`KEY_CHECK_ATTRIB`, `KEY_CHECK_ANY`, `KEY_CHECK_FNMATCH` are defined identically in both classes. The `simple_config_options` class accepts these values but delegates validation to `simple_config_keys`. One of the two definitions is redundant.

**9. `simple_config_editor` uses `cached_property` for the mutable config**

The `_config` attribute is a `cached_property`, loaded once from disk. If the underlying file is modified by another process between editor operations, the editor works from a stale in-memory copy. Mutations are applied and saved through this same stale instance.

**10. Everything is strings**

All values are stored as `str` regardless of content. Typed access requires calling the right method (`get_bool()`, `get_string_list()`). There is no coercion at load time: `enabled: true` and `enabled: yes` and `enabled: 1` are three unrelated strings unless the caller uses `get_bool()`. Type intent is not captured in the config file itself.

**11. Unresolved FIXME**

`simple_config.clone()` has a comment `# FIXME: the options here dont really do anything` and indeed the `sections`, `source`, `check_env_vars`, `entry_formatter`, `section_finder`, and `options` arguments are accepted but the implementation ignores them, always copying from `self`.

---

## Migration proposal: TOML

### Why TOML

- `tomllib` is in the Python stdlib from 3.11 onward (read-only). The project runs on Python 3.14, so it is available unconditionally.
- TOML natively carries types: `42` is `int`, `3.14` is `float`, `true` is `bool`, `"string"` is `str`, `[1, 2]` is `list`. No manual coercion methods needed.
- Standard format with wide tooling support.
- Comments with `#`.
- The one gap: **there is no stdlib TOML writer**. `tomllib` is read-only. A minimal custom serializer is straightforward given the constrained value types this codebase uses.

### Format mapping

| simple_config concept | TOML equivalent |
|---|---|
| Section `name` | `[name]` table |
| `key: value` | `key = "value"` (or typed literal) |
| `${ENV_VAR}` | Post-process strings in loader |
| `fancy extends basic` | `_extends = "basic"` meta-key in `[fancy]` |
| Key annotation `key[flag]` | Separate `[section._annotations]` sub-table |
| Multi-section with same name | `[[array_of_tables]]` |
| `# comment` | `# comment` |

### Basic example

Current format:

```
basic
  color: red
  count: 3
  enabled: true
  tags: foo bar baz

fancy extends basic
  color: blue
```

TOML equivalent:

```toml
[basic]
color = "red"
count = 3
enabled = true
tags = ["foo", "bar", "baz"]

[fancy]
_extends = "basic"
color = "blue"
```

Note that `count`, `enabled`, and `tags` are now typed without any special accessor methods.

### Environment variable interpolation

The `${VAR}` syntax is not native to TOML; TOML does not process string contents. The resolver stays as a post-processing step in the Python loader, applied to any string values after `tomllib.loads()` returns. Behavior is unchanged.

```python
import os
import re

_ENV_PATTERN = re.compile(r'\$\{([^}]+)\}')

def resolve_env_vars(value: str) -> str:
    def replace(match):
        var = match.group(1)
        if var not in os.environ:
            raise KeyError(f'environment variable not set: {var!r}')
        return os.environ[var]
    return _ENV_PATTERN.sub(replace, value)
```

Apply this recursively over all string leaves after loading.

### Section inheritance (`extends`)

TOML has no built-in inheritance. The `_extends` meta-key scheme is handled in a post-processing pass:

```python
import tomllib

def load_config(path: str) -> dict:
    with open(path, 'rb') as file_handle:
        raw = tomllib.load(file_handle)
    return _resolve_inheritance(raw)

def _resolve_inheritance(tables: dict) -> dict:
    resolved = {}
    for name, table in tables.items():
        resolved[name] = _resolve_section(name, tables, resolved, set())
    return resolved

def _resolve_section(name, tables, resolved, visiting):
    if name in resolved:
        return resolved[name]
    if name in visiting:
        raise ValueError(f'circular extends: {name!r}')
    visiting.add(name)
    table = dict(tables[name])
    parent_name = table.pop('_extends', None)
    if parent_name:
        if parent_name not in tables:
            raise KeyError(f'section {name!r} extends unknown section {parent_name!r}')
        parent = _resolve_section(parent_name, tables, resolved, visiting)
        merged = dict(parent)
        merged.update(table)
        table = merged
    resolved[name] = table
    return table
```

The `_extends` key is reserved and stripped from the final dict. Circular dependency detection uses a visiting set, same as the existing `dependency_resolver`.

### Key annotations

Annotations (`key[flag, attr=value]: value`) are a niche feature used to attach metadata to individual keys. TOML has no syntax for per-key metadata. Options:

**Option A — drop annotations entirely.** If the callers of annotations can be audited and none of the active code paths use them, this is the simplest path. Annotated keys appear to be used for hints to formatters/serializers and not for value semantics.

**Option B — separate `_annotations` sub-table.** Each annotated key gets an entry in a parallel table:

```toml
[section]
key = "value"

[section._annotations]
key = "flag, attr=value"
```

This keeps annotations out of the value namespace, allows the loader to reconstruct them, and round-trips cleanly.

**Option C — inline tables for annotated keys.** Represent the value and its annotations together:

```toml
[section]
key = { value = "actual_value", annotations = "flag, attr=value" }
```

This is more explicit but breaks the simple `key = value` contract for annotated keys. Typed accessors become less ergonomic.

**Recommendation: Option A**, after first auditing all call sites of `has_annotation()` and `find_annotation()`. If annotations are only used by a formatter and not for conditional logic, they can be dropped without behavior loss.

### Multiple sections with the same name

The current format allows:

```
targets linux
  arch: x86_64

targets macos
  arch: arm64
```

(Two sections both named `targets`, distinguished by `extra_text`.)

TOML arrays of tables handle this:

```toml
[[targets]]
platform = "linux"
arch = "x86_64"

[[targets]]
platform = "macos"
arch = "arm64"
```

The `targets` key in the parsed dict becomes a `list` of dicts. This is a semantic change: the `extra_text` field of the section header becomes a first-class key inside each table entry. Callers that use `find_all_sections()` and inspect `section.header_.extra_text` need updating.

If the codebase rarely uses multiple same-named sections, it may be simpler to forbid them in TOML files and move any current uses to a keyed approach (`[targets.linux]`, `[targets.macos]`).

### Strong typing: what changes at the call site

The existing typed accessors become redundant for the common cases:

| Old code | New code |
|---|---|
| `section.get_bool('enabled')` | `section['enabled']` — already `bool` |
| `section.get_value('count')` returns `"3"` | `section['count']` — already `int` |
| `section.get_string_list('tags')` | `section['tags']` — already `list[str]` |
| `section.get_value('path')` | `section['path']` — `str`, env vars resolved by loader |

The only typed accessor that stays meaningful is env-var resolution, which is applied uniformly to all strings by the loader.

### What a minimal TOML writer looks like

Since `tomllib` is read-only, a writer is needed for `save()` and `to_string()`. The value types in this codebase are a small subset of full TOML:

```python
def _toml_value(value) -> str:
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, list):
        items = ', '.join(_toml_value(item) for item in value)
        return f'[{items}]'
    raise TypeError(f'unsupported TOML value type: {type(value)}')

def write_toml(tables: dict) -> str:
    lines = []
    for section_name, table in tables.items():
        lines.append(f'[{section_name}]')
        for key, value in table.items():
            lines.append(f'{key} = {_toml_value(value)}')
        lines.append('')
    return '\n'.join(lines)
```

This covers the existing value space (strings and booleans from `get_bool()`). As typed usage expands, int, float, and list support rounds it out.

### Features to preserve as-is (in a compatibility layer)

| Feature | Strategy |
|---|---|
| Source origin tracking (file + line) | `tomllib` does not expose line numbers. Errors cite the TOML key path (`section.key`) instead. The `simple_config_error` class can carry a key-path string rather than a `(source, line_number)` pair. |
| `simple_config_files` multi-file loading | Keep the search-path and glob logic; replace per-file parsing with `tomllib.load()`. `extends` resolution across files uses the same topological sort. |
| `simple_config_editor` | Simplify: load with `tomllib`, modify the dict in memory, serialize with the custom writer. Remove the `cached_property` in favor of explicit reload on demand or a dirty flag. |

### Features that can be dropped

- `__getattr__` magic on `simple_config` and `simple_config_section` — attribute-style access is fragile and causes the silent section-creation bug. Dict-style access (`config['section']['key']`) is explicit and safe.
- `key_check_type` / `simple_config_keys` — TOML keys are always identifiers; the parser enforces this. The `fnmatch` mode for glob-pattern keys does not translate to TOML at all and should be evaluated separately.
- `namedtuple` for `simple_config_section` — a plain `dataclass` or `dict` suffices and is honestly more appropriate for a mutable container.
- `simple_config_variables` class — the variable scoping concept survives as a plain `dict` merged with `os.environ` at resolve time.

---

## Real-world usage analysis

Reading the actual callers across `bat`, `eca`, `rebuild`, and `rehack` reveals that `simple_config` is used in several distinct modes that do not all have the same migration path.

### Usage pattern A — Structured config (clean TOML candidate)

The most common pattern: load a file, find a section by name, call `to_dict()`, use the values.

| File | What it does |
|---|---|
| `bat/vfs/vfs_config.py` | Loads `fsconfig` section, `to_dict()` → extract `vfs_type` and remaining values |
| `rebuild/config/storage_config_manager.py` | Loads `storage` sections, each becomes a `storage_config` object |
| `bat/computer_setup/computer_setup_manager.py` | Iterates all sections, each section drives a task |
| `eca/binary_builder/binary_builder_secrets_baker.py` | Iterates all sections, each drives a vault secret bake |
| `eca/job_executor/job_executor.py` | Finds a named section, reads `branch` key |
| `bes/bcli/bcli_options.py` | Loads a named section, maps known keys to option fields |
| `rehack/testing/retest_runner.py` | Reads `environment` section, two string-list keys |
| `eca/astral/engine_version/engine_version.py` | Read/write of Perforce-stored config; round-trip via `str(config)` |
| `eca/ci/ci_env_fake.py` and `ci_v2_*` | Round-trip: build in memory, serialize, deserialize |

All of these use `simple_config` purely as a key-value store. None of them rely on `extra_text`, annotations, fnmatch keys, or duplicate keys. They migrate cleanly to TOML + `bdata_class_base`.

### Usage pattern B — Section name carries metadata via `extra_text`

Three callers use the section header's `extra_text` field as a first-class value, not as documentation.

**`bat/ssh/config/ssh_config_file.py`** uses `simple_config` to model `~/.ssh/config`, where the format is:

```
Host someserver.example.com
  IdentityFile ~/.ssh/id_rsa
  User git
```

Here `someserver.example.com` is stored as `header_.extra_text`. The key/value separator is a space (not `:`), requiring a custom `entry_parser` and `entry_formatter`. The file format is fixed by the SSH spec — it cannot become TOML.

**`bat/git/git_temp_repo.py`** is the most extreme case. It uses `simple_config` as a **test fixture DSL**, not a config file at all. The section name is a command type (`file`, `add`, `tag`, `branch`, `remove`, `push`), and `extra_text` carries positional command arguments:

```
file foo.txt
  content: hello world
  perm: 0o644

add alias1 commit_name
  foo.txt: content

tag v1.0 alias1
  from_commit: @alias1
  push: true
```

The `_command_parse_add` method reads `entry.annotations` (`perm` annotation on files) directly. This is the only active caller of the annotations feature in the codebase. Neither the DSL semantics nor the positional header arguments map to TOML at all. This usage should remain as-is with the existing `simple_config`.

### Usage pattern C — `__getattr__` attribute access on sections

Several callers use dot-access on sections as if they were objects:

```python
# downloader.py
section.method    # 'git' or 'http'
section.version   # a string
section.address   # a URL

# dim_config.py
self.config.system_name
self.config.system_version
self.config.image_version
self.steps.section(step_name).version
```

This relies on `simple_config_section.__getattr__` routing to `find_by_key()`. In a TOML-backed design, these become `section['method']` dict lookups or typed dataclass attributes. No features are lost; it is purely a call-site syntax change.

### Usage pattern D — Non-identifier keys (`KEY_CHECK_ANY`)

Two callers explicitly opt out of key validation.

**`eca/script/modules/script_module_app_version.py`** stores iOS version data keyed by branch name:

```
major_app_version
  master: 1
  release-beta-3.2: 3

short_version_string
  master: 1.0
  release-beta-3.2: 3.2
```

Branch names (`release-beta-3.2`) are not valid Python identifiers. TOML supports quoted keys (`"release-beta-3.2" = 3`) which handles this case.

**`eca/appcenter/appcenter.py`** calls `simple_config.from_file(config_file, validate_key_characters=False)` — but **`validate_key_characters` is not a valid parameter of `simple_config.from_file()`**. This call would raise `TypeError` at runtime. It is a latent bug. The actual keys in those config files are email addresses and app names, which also need quoted-key TOML syntax.

### Usage pattern E — Duplicate keys and `get_all_values()`

**`bat/computer_setup/computer_setup_manager.py`** uses:

```python
for next_values in section.get_all_values('value'):
    task_values.extend(key_value_list.parse(next_values))
```

The config file contains multiple `value:` entries per section:

```
some_task
  class: MyTaskClass
  value: foo=1
  value: bar=2
  value: baz=3
```

TOML forbids duplicate keys. This must be expressed as an array:

```toml
[some_task]
class = "MyTaskClass"
value = ["foo=1", "bar=2", "baz=3"]
```

The reading code changes to `section['value']` returning a `list[str]`, which is actually simpler.

### Usage pattern F — `apple_store` uses `simple_config` as a mutable in-memory data structure

`eca/appcenter/apple_store.py` is the most complex caller. It does not use `simple_config` as a config file format at all. It uses it as an **ordered, mutable key-value store** with custom entry formatting:

```python
config = simple_config(entry_formatter=self.__class__.sorted_lines_entry_formatter)
testers_section = config.add_section('TESTERS')
apps_section = config.add_section('APPS')
# ... dynamically builds the in-memory structure ...
# ... then uses match_by_key('{},*'.format(email)) with fnmatch to find entries ...
# ... then deletes and re-adds entries ...
# ... then saves to file or compares against another config ...
```

Key operations that have no TOML equivalent:
- `section.match_by_key('{},*'.format(email))` — fnmatch lookup on keys
- `section.match_entry(pattern)` — finding an entry by key pattern
- `section.delete_value(key)` / `section.add_value(key, value)` live mutation
- Multi-line values: a tester's groups are stored as newline-separated text in a single value
- Custom per-entry formatters (`sorted_lines_entry_formatter`)
- `entry.origin.source` / `entry.origin.line_number` used in `_describe_problem_area()`

This is not a config file use case. It is a custom data structure built on top of `simple_config`. The correct migration here is not to TOML — it is to replace it with an explicit data model (e.g., a `dataclass` for tester/app/group relationships) that does not lean on `simple_config` at all.

### Usage pattern G — `simple_config` passed as an API parameter

`downloader.download(section)` accepts a `simple_config_section` directly. `script_module_downloader` type-checks the argument with `check.check_simple_config_section()`. This means the section object is part of the calling contract between modules.

Migrating requires either changing the API to accept a typed dataclass instead, or keeping `simple_config_section` as the internal representation while adding a `from_toml_dict()` constructor.

### Bugs found in callers

**`appcenter.py` lines 215 and 293** — `simple_config.from_file(config_file, validate_key_characters=False)` passes an unknown keyword argument that does not exist in `simple_config.from_file()`. This is a `TypeError` at runtime for any path that calls `org_sync_config_app_groups` or `org_sync_config_org_groups`.

**`apple_store.py` line 386** — Same `validate_key_characters=False` bug.

**`storage_config_manager.py` line 33** — `raise self.error('storage with name "%s" already exists.', section.origin)` — `simple_config_error.__init__` takes `(message, origin)` as positional args, but the format string uses `%s` which is not applied (Python would need `%` operator or `.format()`). The origin is passed as the second positional arg which is correct, but the `%s` in the message is never replaced — the string literal `'storage with name "%s" already exists.'` is emitted verbatim.

---

## Revised migration tiers

Based on the real-world usage analysis, a clean migration requires treating different usages separately.

### Tier 1: Migrate to TOML + `bdata_class_base`

These callers use `simple_config` as a pure structured config format and have no dependency on `extra_text`, annotations, fnmatch keys, duplicate keys, or mutable in-memory manipulation.

- `bat/vfs/vfs_config.py`
- `rebuild/config/storage_config_manager.py`
- `eca/binary_builder/binary_builder_secrets_baker.py`
- `eca/job_executor/job_executor.py`
- `bes/bcli/bcli_options.py`
- `rehack/testing/retest_runner.py`
- `eca/astral/engine_version/engine_version.py`
- `eca/ci/ci_env_fake.py`, `ci_v2_env_fake_git.py`, `ci_v2_env_fake_perforce.py`, `ci_v2_detect.py`
- `eca/script/modules/script_module_app_version.py` (needs quoted TOML keys)
- `eca/download/downloader.py` (once its API is changed to accept a dataclass)
- `bat/computer_setup/computer_setup_manager.py` (duplicate `value` keys → TOML array)

For each of these, the migration is:
1. Define a `@dataclass` inheriting `bdata_class_base` for each section type.
2. Load the file with `tomllib.load()`.
3. Call `SectionClass.parse_json_dict(raw['section_name'])` to get a typed object.
4. Replace `section.get_value('key')` / `section.get_bool('key')` with typed field access.
5. Replace the config file with a `.toml` file.

### Tier 2: Keep `simple_config`, fix bugs

These callers use features that TOML cannot express and are not worth re-architecting as part of a config migration.

- `bat/ssh/config/ssh_config_file.py` — SSH config format is fixed by spec. Keep `simple_config` with its custom parser/formatter. Fix the `cached_property` reload issue.
- `bat/git/git_temp_repo.py` — It is a test DSL, not a config file. Keep as-is.
- `eca/script/script_runner.py` — Uses `simple_config` to define custom arg types via section metadata. Not a config file pattern.
- `bat/docker_image_maker/dim_config.py` — Loads multiple heterogeneous config files; should migrate to TOML but may be low priority.

### Tier 3: Replace `apple_store`'s usage with a proper data model

`eca/appcenter/apple_store.py` needs to be rewritten to use an explicit data model rather than `simple_config` as an in-memory store. The fnmatch key lookup, multi-line values, and custom formatters are symptoms of using the wrong tool. A proper `dataclass` for `tester`, `app`, and `group` relationships, and a TOML or JSON file for the config format, is the correct solution.

---

## Migration order of operations

1. **Audit annotation callers** — grep for `has_annotation`, `find_annotation`, `annotations` across the full codebase to decide Option A/B/C.
2. **Audit `extra_text` callers** — determine if multi-section-same-name is used and how `extra_text` is consumed.
3. **Write `toml_config` loader** — `load()` → `tomllib` + `_resolve_inheritance()` + `resolve_env_vars()`.
4. **Write the minimal TOML serializer** — enough for `save()` and `to_string()`.
5. **Port `simple_config_files`** — swap per-file parser, keep search path and dep resolution logic.
6. **Port `simple_config_editor`** — simplify by removing `cached_property`.
7. **Migrate config files** — convert existing `.cfg` / `.conf` files to `.toml`.
8. **Update callers** — replace `section.get_bool(key)` with `section[key]`, etc.

---

## Custom types and `bdata_class_base`

### The pattern

Each config section maps to a Python `dataclass` that inherits from `bdata_class_base`. The TOML loader returns a plain `dict`; `parse_json_dict()` constructs the typed object from it. `to_dict()` serializes it back for the TOML writer. This is the same round-trip that the rest of the codebase uses for JSON persistence.

```python
import dataclasses
import pathlib
from bes.data_classes.bdata_class_base import bdata_class_base

@dataclasses.dataclass
class rip_config(bdata_class_base):
  output_directory: pathlib.Path
  max_retries: int
  enabled: bool
  formats: list[str]
```

TOML file:

```toml
[rip]
output_directory = "~/music"
max_retries = 5
enabled = true
formats = ["flac", "wav"]
```

Loading:

```python
import tomllib

with open('config.toml', 'rb') as file_handle:
    raw = tomllib.load(file_handle)

config = rip_config.parse_json_dict(raw['rip'])
config.output_directory   # pathlib.Path('~/music')
config.max_retries        # 5   — int
config.enabled            # True — bool
config.formats            # ['flac', 'wav']
```

`tomllib` already gives you `int`, `bool`, and `list` for free. The only field that needs a conversion step here is `output_directory`, because TOML stores it as a string and the application wants a `pathlib.Path`.

### Conversion hooks

`bdata_class_base` provides two overrideable classmethods for exactly this:

- `from_dict_hook(d)` — called by `parse_json_dict()` before construction. Transform raw TOML values (strings, ints, etc.) into application types.
- `to_json_dict_hook(d)` — called by `to_dict()` after `dataclasses.asdict()`. Transform application types back into TOML-serializable primitives.

```python
@dataclasses.dataclass
class rip_config(bdata_class_base):
  output_directory: pathlib.Path
  max_retries: int
  enabled: bool
  formats: list[str]

  @classmethod
  def from_dict_hook(clazz, d):
    d = dict(d)
    d['output_directory'] = pathlib.Path(d['output_directory'])
    return d

  def to_json_dict_hook(self, d):
    d['output_directory'] = str(d['output_directory'])
    return d
```

The hooks are the only place type conversion lives. The dataclass fields and the TOML file stay clean.

### Enum fields

`bdata_class_base.parse_json_dict_field_enum()` already handles the string→enum direction. Call it inside `from_dict_hook`:

```python
import dataclasses
import enum
from bes.data_classes.bdata_class_base import bdata_class_base

class audio_format(enum.Enum):
  flac = 'flac'
  wav = 'wav'
  mp3 = 'mp3'

  @classmethod
  def parse(clazz, value: str) -> 'audio_format':
    try:
      return clazz(value)
    except ValueError:
      raise ValueError(f'unknown audio format: {value!r}')

@dataclasses.dataclass
class rip_config(bdata_class_base):
  output_directory: pathlib.Path
  default_format: audio_format

  @classmethod
  def from_dict_hook(clazz, d):
    d = dict(d)
    d['output_directory'] = pathlib.Path(d['output_directory'])
    d['default_format'] = clazz.parse_json_dict_field_enum(audio_format, d, 'default_format')
    return d

  def to_json_dict_hook(self, d):
    d['output_directory'] = str(d['output_directory'])
    d['default_format'] = self.field_to_enum_value(d['default_format'])
    return d
```

TOML:

```toml
[rip]
output_directory = "~/music"
default_format = "flac"
```

The string `"flac"` comes in from TOML, `from_dict_hook` converts it to `audio_format.flac`, and `to_json_dict_hook` converts it back to `"flac"` for writing. The enum's string representation stays in the file.

### Nested sections as a top-level config object

Each TOML table becomes its own dataclass. A top-level config class holds all sections as typed fields and wires up the hooks for each:

```python
@dataclasses.dataclass
class full_config(bdata_class_base):
  rip: rip_config
  cddb: cddb_config

  @classmethod
  def from_dict_hook(clazz, d):
    d = dict(d)
    d['rip'] = rip_config.parse_json_dict(d['rip'])
    d['cddb'] = cddb_config.parse_json_dict(d['cddb'])
    return d

  def to_json_dict_hook(self, d):
    d['rip'] = self.rip.to_dict()
    d['cddb'] = self.cddb.to_dict()
    return d
```

Loading the whole file becomes a single call:

```python
with open('config.toml', 'rb') as file_handle:
    raw = tomllib.load(file_handle)
config = full_config.parse_json_dict(raw)
config.rip.output_directory    # pathlib.Path
config.rip.default_format      # audio_format.flac
config.cddb.server             # str
```

### Integrating with the `check` type system

Call `register_check_class()` at module level on each config class. This is the same pattern used everywhere else in the codebase:

```python
rip_config.register_check_class()
cddb_config.register_check_class()
full_config.register_check_class()
```

This gives `check.check_rip_config()`, `check.is_rip_config()`, and the seq variants for free.

### Defaults

`dataclass` `field(default=...)` and `field(default_factory=...)` provide defaults without any special loader logic. Optional fields that may be absent from the TOML file work cleanly with `typing.Optional` and a `None` default:

```python
@dataclasses.dataclass
class rip_config(bdata_class_base):
  output_directory: pathlib.Path
  max_retries: int = 3
  enabled: bool = True
  formats: list[str] = dataclasses.field(default_factory=lambda: ['flac'])
  log_file: typing.Optional[pathlib.Path] = None
```

`parse_json_dict()` already filters to known field names (`filtered_data = {key: value for key, value in hooked_d.items() if key in field_names}`), so TOML keys that don't correspond to a field are silently ignored rather than causing a constructor error. Fields absent from the TOML file get their dataclass defaults.

### What changes at the call site

Old pattern with `simple_config`:

```python
config = simple_config.from_file('config.cfg')
output_dir = pathlib.Path(config.rip.output_directory)   # manual Path conversion
max_retries = int(config.rip.max_retries)                # manual int conversion
enabled = config.rip.get_bool('enabled')                 # special accessor
formats = config.rip.get_string_list('formats')          # special accessor
fmt = audio_format.parse(config.rip.get_value('default_format'))  # manual enum
```

New pattern:

```python
config = full_config.parse_json_dict(tomllib.load(...))
output_dir = config.rip.output_directory    # pathlib.Path, no cast
max_retries = config.rip.max_retries        # int, no cast
enabled = config.rip.enabled               # bool, no cast
formats = config.rip.formats               # list[str], no cast
fmt = config.rip.default_format            # audio_format, no cast
```

All type conversions are concentrated in `from_dict_hook` on each dataclass, written once, tested once.
