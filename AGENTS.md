# Repository Guidelines

Single English contributor and agent guide. Follow this file unless the user overrides it.

## Project Structure & Module Organization

`ALPHA3.py` is the CLI entry point and encoder dispatcher. Root helpers are `encode.py`, `charsets.py`, `io.py`, and `print_functions.py`. Architecture-specific encoders and decoder assets live under `x86/` and `x64/`, grouped by encoding, casing, address mode, and register target, for example `x64/ascii/mixedcase/rm64/RAX.bin`. Tests and sample shellcode live in `test/`. `TREE.md` records the file tree; `NAVIGATION.md` records status, implemented features, and key addresses.

## Build, Test, and Development Commands

- `python3 ALPHA3.py --help`: list supported encoders and usage.
- `python3 -m compileall -q .`: syntax-check all Python modules.
- `python3 test/validate_x64_shellcode.py`: run x64 emulator validation; requires `unicorn`.
- `python3 ALPHA3.py x86 ascii mixedcase eax --input=test/w32-writeconsole-shellcode.bin --output=/tmp/alpha3-x86.bin`: smoke-test x86 encoding.
- `python3 ALPHA3.py x64 ascii mixedcase rax --input=test/w64-writeconsole-shellcode.bin --output=/tmp/alpha3-x64.bin`: smoke-test x64 encoding.

NASM is optional because `.bin` decoders are committed; use it only to regenerate missing binaries from `.asm`.

## Coding Style & Naming Conventions

This is a Python 3 port of legacy ALPHA3 code. Preserve local style: root modules commonly use two-space indentation and procedural functions such as `ParseCommandLine()`. Keep binary data as `bytes` at I/O boundaries and decode only for display. Encoder paths and filenames mirror architecture/register semantics.

## Testing Guidelines

Run `compileall` for Python changes. For encoder changes, also run the relevant smoke command and `test/validate_x64_shellcode.py` when x64 behavior may be affected. Built-in `--test` depends on Windows/Testival. For docs-only changes, code verification may be skipped, but say so.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `Port ALPHA3 to Python 3` and `Fix bug in PrintLine()`. Keep commits focused and mention affected architecture or charset. PRs should include change summary, validation commands, platform notes, and regenerated `.bin` artifacts.

When asked to commit or prepare one, update `NAVIGATION.md` for status, key locations, and verification records; `TREE.md` for the current tree; and `README.md` only for necessary user-visible usage or verification changes. Before committing, confirm `REVIEW.md` has been backed up and cleared when the review workflow applies.

## Agent Workflow Rules

Before inspection, edits, or commit preparation, read `TREE.md` and `NAVIGATION.md`, then choose a narrow scope to avoid repeated exploration or accidental compatibility-file changes. Keep changes focused, do not roll back unrelated user or agent edits, and treat historical decoder assets, `.bin`, `.asm`, and Testival files carefully. Build/test caches must not be version-controlled.

For code review, bug inspection, regression checks, shellcode validation, or other quality checks, write results to `REVIEW.md`. Each finding must include location, description, fix action, and verification method. If fixed, record the fix; if deferred, record reason, risk, and follow-up. Do not replace `REVIEW.md` in the same work cycle.

After a review cycle, back up `REVIEW.md`: ensure it contains all findings, fixes, and verification results; create `./backup/`; count existing `Review-xx.md` files; write the next `Review-xx.md` using two digits from `01` to `99`, defaulting to count plus one and using the next available number if needed. After confirming the backup, clear `REVIEW.md` and leave it empty. `backup/` is local, ignored by `.gitignore`, and not version-controlled. If numbering exceeds `99`, stop for manual handling; never overwrite old backups.
