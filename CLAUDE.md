# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Documentation layout

- **`docs/`** — primers, FAQs, and reference material. Stable, user-facing, topic-focused. Examples: `ripping-offset.md`.
- **`claude-docs/`** — working documents that Claude and Ramiro collaborate on for features in progress: design proposals, migration plans, analysis. Example: `RIPPER.md`. These are living documents and may be incomplete or speculative.

## Licensing

**Always flag GPL code before copying it into this project.** If logic from a GPL-licensed project (e.g. whipper, cdparanoia) is being considered for direct inclusion, stop and flag it explicitly. Using GPL software as an external subprocess is fine — that does not create a licensing obligation. Copying GPL source into this codebase does.

## Code Style

- **Indentation**: 2 spaces throughout (no tabs).
- **Python version**: The runtime is Python 3.14, but avoid features introduced in 3.13 or 3.14 unless absolutely necessary.
- **Imports**: Use `import <package>` and refer to names with the full namespace (`rich.progress.BarColumn`, not `from rich.progress import BarColumn`). This applies to all packages, not just `rich`. For intra-project relative imports, use `from . import module` and refer to names as `module.Name` — never import individual functions, constants, or non-class names from a sibling module (`from .module import func` is forbidden).
- **All imports go at the top of the file.** Never use deferred/inline imports inside functions or methods (`from x import y` inside a def). Top-level imports are mandatory — they catch circular dependencies and missing modules immediately at load time rather than at runtime deep in a call stack.
- **No abbreviations in identifiers or filenames.** Spell words out in full: `musicbrainz` not `mb`, `accurate_rip` not `ar`, `command` not `cmd`, `directory` not `dir` in names (though `dir` is fine in local variables). Apply this to module names, class names, and function names.
- **Never create `__init__.py` files.** This project does not use them.
- **Classmethods use `clazz` not `cls`** as the first parameter name.
- **Filename/extension operations**: Always use `bf_filename` (`bes.files.bf_filename`) for any filename or extension check or manipulation — `bf_filename.extension()`, `bf_filename.has_extension()`, `bf_filename.has_any_extension()`, etc. Never use raw `os.path.splitext`, `str.endswith`, or manual string slicing for extension work.

## Commands

- **Run the app**: `./r bin/<app>.py <args>` — uses `uv run` with the correct PYTHONPATH
- **Run all tests**: `./t`
- **Run a single test file**: `./t tests/lib/bes/files/test_bf_entry.py`
- **Run a single test**: `./t tests/lib/bes/files/test_bf_entry.py -k test_absolute_filename_only`
- **Run tests in parallel**: `./t -n auto`

**Always use `./t` to run unit tests, never `./r`.** `./t` invokes pytest with the correct setup. `./r` is only for running application scripts.

## PYTHONPATH / Dependencies

The `./r` script sets up `PYTHONPATH` to include sibling project `lib/` directories (`bes`, `bav`, `bnet`) alongside this project's `lib/`. All runs must go through `./r` to have the correct path. Python 3.12 is required (`env/python.version`).

### Testing
- Tests live in `tests/lib/<name>/`.
