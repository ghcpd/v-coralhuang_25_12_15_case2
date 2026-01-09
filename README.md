# Refactor PR: Consolidate Tool Logic

This change refactors the duplicated tool implementations into a small, testable, and well-separated implementation.

What was refactored
- Extracted shared validation, payload building, transport and logging into `refactored_tools.base.BaseTool` and `refactored_tools.client`.
- Implemented `ToolA`, `ToolB`, and `ToolC` as thin subclasses in `refactored_tools.tools` that share behavior and consistent payload formatting.
- Added a small test suite (`tests/test_tools.py`) validating valid/invalid behavior, consistent payload formatting, and basic logging.
- Added `run_tests` (and `run_tests.bat` for Windows) which runs the tests and exits non-zero on failure.

Before / After
- Before: `input_tools.py` contained three implementations with duplicated validation and inconsistent payload naming/semantics.
- After: `refactored_tools/` contains a single, well-tested implementation that centralizes validation and formatting rules and preserves public method signatures and return structure.

How to run tests
1. From the repository root run (cross-platform):

   python run_tests

   On Windows you can also run `run_tests.bat`.

2. The command will run the `unittest` test suite and exit with a non-zero status if any test fails.

Assumptions and tradeoffs
- Compatibility: We preserved public `run` method signatures and the return value structure (`{"ok": bool, ...}`), while making validation rules uniform. Error messages have been standardized for clarity.
- Transport: A small in-repo `HttpClient` shim is included (mirroring the original `input_tools.HttpClient`) so the refactor is self-contained and deterministic in tests.
- Scope: The goal was to reduce duplication and improve correctness and readability with minimal changes and no edits to existing input files. If consumer code depended on the original module-level logging or exact error message text, slight changes may be observed; behavior and signatures are otherwise compatible.
