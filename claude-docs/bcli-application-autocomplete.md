# bcli_application bash autocomplete

## Goal

When a user types `rmusic1.py <TAB>` or `rmusic1.py ocr <TAB>` in a bash shell, they get completions for top-level commands, sub-commands, and flags.

## How bash completion works

Bash calls a registered shell function when the user presses TAB. That function must populate `COMPREPLY` with the list of valid completions for the current word. The standard pattern for Python CLIs is to have the program print its own completions when invoked with a special flag, and have a thin shell function call it:

```bash
_rmusic_complete() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=($(compgen -W "$(rmusic1.py --bcli-complete "$COMP_CWORD" "${COMP_WORDS[@]}")" -- "$cur"))
}
complete -F _rmusic_complete rmusic1.py
```

## The heavy-import problem

Factories in this codebase use **deferred imports inside `add_commands`** to avoid loading expensive modules at startup:

```python
def add_commands(self, subparsers):
    def _add_common_options(p):
        from . import rmusic_ocr_engine          # pulls in tesseract, easyocr
        from . import rmusic_ocr_layout_detector
```

The `docling_layout` and `surya` factories are even heavier — importing those modules triggers multi-second model-loading code. Calling `add_commands` at TAB time to extract flag names would make completion unacceptably slow.

This rules out the obvious approach of "build the argparse parser on demand and read `_actions`" for flag completion.

## Chosen approach: baked-static completion script

`--bcli-generate-completion bash` walks all registered factories **once**, builds every parser, harvests all flag strings, and bakes them directly into the generated shell script as static `compgen -W "..."` word lists — one per (command, subcommand) pair.

The result is a self-contained bash script with no runtime Python call at all:

```bash
# rmusic1.py bash completion  (generated — re-run to refresh)
_rmusic1_py_complete() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    local cmd="${COMP_WORDS[1]}"
    local subcmd="${COMP_WORDS[2]}"

    case "$cmd" in
        ocr)
            case "$subcmd" in
                detect_file|detect_dir|detect_columns)
                    COMPREPLY=($(compgen -W "--engine --language --layout --overwrite \
                                             --no-orientation --output --show --save \
                                             --tiff --side-by-side" -- "$cur"))
                    return ;;
            esac
            COMPREPLY=($(compgen -W "detect_orientation detect_file detect_dir detect_columns" -- "$cur"))
            return ;;
        docling_layout)
            ...
    esac

    COMPREPLY=($(compgen -W "accurate_rip acoustid albums artwork cddb ..." -- "$cur"))
}
complete -o default -F _rmusic1_py_complete rmusic1.py
```

TAB response time is then the cost of forking bash — effectively instant. The heavy Python imports never happen during completion.

**Trade-off**: the script goes stale when flags change. The user re-runs `--bcli-generate-completion bash` to refresh. This is the same model used by tools like `pip`, `rustup`, and `kubectl`.

## Entry points in bcli_application

### `--bcli-generate-completion bash`

Detected early in `run()`, before normal parsing. Builds every registered parser (paying the heavy-import cost once), collects all flag strings per (command, subcommand), emits the baked shell script to stdout, exits 0.

This is the only time heavy imports are triggered by the completion system.

### `--bcli-complete <cword> <word0> <word1> …` (optional, lightweight)

A dynamic fallback for users who prefer not to manage a generated script. Only completes top-level command names and sub-command names — never flags. Walks only `bcli_parser_tree` (zero heavy imports). Prints one candidate per line.

The baked script approach is preferred; this exists as a simpler opt-in.

## What changes where

### `bcli_parser_tree`

Add one method: `children_at(path) -> list[str]` — returns child node names at the given path, or `[]` if missing. Used by both the dynamic completer and the script generator to enumerate commands and sub-commands without touching `_root`/`children` directly.

### `bcli_application`

In `run()`, before the existing `if not args` check, inspect `args[0]`:

- `--bcli-generate-completion`: call `_generate_completion_script(shell)`, print, return 0.
- `--bcli-complete`: call `_complete(cword, words)`, print, return 0.

### New module: `bcli_completer`

Holds both pieces of logic as standalone functions, separately testable:

```
bcli_completer.generate_script(parser_manager, prog_name) -> str
bcli_completer.complete(parser_tree, cword, words) -> list[str]
```

`generate_script` is the one that builds all parsers and bakes flags. `complete` is the lightweight dynamic path (no parser construction).

### `bcli_command_factory_i`

No changes required. The generator calls the same `add_arguments` / `add_commands` path that normal parsing uses — it just does it offline at script-generation time.

## What is NOT needed

- No shell script files to ship or install.
- No third-party libraries (`argcomplete`, `click`, etc.).
- No changes to any factory or handler.
- No changes to the deferred-import pattern inside factories.

## Edge cases

**Flags with values** (`--output /some/path`): after such a flag bash gets empty `COMPREPLY` and falls back to filename completion via `-o default`. Correct.

**`--` separator**: the baked case statement can check for `--` in the prefix and stop offering flags once seen.

**Unknown prefix word**: emit nothing, exit cleanly, never error.

**Script staleness**: the generated script includes a comment with a generation timestamp and the command to re-run it, so users know when it was last refreshed.

## Activation

```bash
# generate once and source on login
rmusic1.py --bcli-generate-completion bash > ~/.rmusic_completion.bash
echo 'source ~/.rmusic_completion.bash' >> ~/.bashrc
```
