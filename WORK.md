# WORK

## Iteration 1
Scope: Add initial tests, docs, and an example-based functional check for the existing uzcy implementation.

Plan:
- Add unit tests covering every function in `uzcy`.
- Add a functional test that runs the CLI against example fixtures.
- Create minimal project docs and a `test.sh` runner.
- Run tests and record results here.

Results:
- Tests: `./test.sh` (ruff check/format, pytest: 72 passed).
- Notes: fixed default exclude handling when `--exclude` is omitted; added docs, tests, examples, and test runner.

Wait, but...
- Double-checked that `--exclude ""` still disables excludes; kept behavior while restoring defaults.
