# Refactor: Agent Tools

This change introduces a refactored implementation of the agent tools used to
construct and send HTTP requests. The goals were to remove duplication,
improve clarity, and ensure consistent validation and payload formats while
keeping the public tool interfaces and return structures compatible.

---

What was refactored and why
- Extracted shared responsibilities into a single, well-tested implementation:
  - Unified input validation
  - Consistent payload construction
  - Centralized logging and transport handling

- Rationale: the original repository contained three tool implementations with
  copy-pasted and inconsistent logic (different validation rules, different
  payload key names, and minor differences in error handling). This made the
  code error-prone and hard to maintain.

Before / After structure
- Original (unchanged, provided input files):
  - `input_tools.py` (original implementations — left untouched)
  - `input_demo.py`

- New (refactored implementation added as new files):
  - `refactored_tools.py` — shared implementation and the three tool classes
    (`ToolA`, `ToolB`, `ToolC`) with identical public signatures to the
    originals.
  - `tests/test_refactored_tools.py` — small unit test suite covering valid
    and invalid inputs and verifying consistent payload formatting.
  - `run_tests` — executable script that runs the tests and exits non-zero on
    failure.

Key design decisions
- Shared validation rules
  - user_id: must be a non-empty string
  - query: must be a non-empty string after stripping whitespace
  - limit: must be an integer > 0

- Consistent payload format
  - All tools now send payloads using camelCase keys: `userId`, `query`,
    `limit`, `tool` (the last indicates A/B/C).
  - Queries are stripped of surrounding whitespace before sending.

- Logging and transport
  - Preserved the basic logging behaviour: each tool prints a single JSON
    payload line prefixed like `[ToolA] request=` to match the original
    format.
  - A small simulated `HttpClient` is included to make tests deterministic.

Compatibility notes and assumptions
- No input files were modified. The original `input_tools.py` remains in the
  repository untouched as required.
- The refactored tools preserve the public constructor signatures and the
  `run(user_id, query, limit=..., timeout_s=...) -> Dict[str, Any]` method
  signature and return shape (i.e. `{"ok": True/False, ...}`).
- Error messages for validation and transport errors are consistent across
  tools; callers should check `ok` and inspect `error`/`raw` as needed.

How to run the tests
1. From the repository root run:

   python run_tests

   The script will run the included unittest suite. It exits with a non-zero
   exit code if any test fails.

Files added
- `refactored_tools.py` — refactored implementation
- `tests/test_refactored_tools.py` — unit tests
- `run_tests` — test runner

Tradeoffs and further improvements
- The simulated `HttpClient` in `refactored_tools.py` keeps tests hermetic and
  avoids introducing third-party dependencies. If integration with a real HTTP
  library is required (e.g. `requests` or `httpx`), the `HttpClient` can be
  replaced or extended without changing the tool interfaces.
- This change intentionally focuses on improving internal structure and test
  coverage. If required, a follow-up change could introduce finer-grained
  logging, structured exceptions, or richer response parsing.

---

If you want the refactored tools to be used by the existing `input_demo.py`, a
small compatibility wrapper can be added that re-exports the new classes under
the original module name. I avoided changing any provided files to respect the
task constraints.
