# Refactor: Agent Tools

## Summary

Refactored the duplicated tool implementations into a shared, testable structure.

What changed:
- Extracted shared validation, payload construction, logging, and transport into `refactored/tools.py`.
- Implemented `BaseTool` and retained public `ToolA`, `ToolB`, and `ToolC` classes to preserve interfaces.
- Standardized validation rules (non-empty `user_id`, non-empty `query`, and `limit > 0`) and payload format (`userId`, `query`, `limit`, `tool`).
- Added unit tests in `tests/test_refactor.py` and an executable `run_tests` script.

## Before / After

Before:
- `input_tools.py` contained three `Tool` classes with duplicated and inconsistent logic across validation, payload keys, and error handling.

After:
- `refactored/tools.py` centralizes that logic. Public tool classes keep the same constructor and `run` signature and return format.

## Design decisions & tradeoffs

- Validation is unified to be strict: `limit` must be > 0 (this fixes inconsistencies and two buggy behaviors in the original code).
- Payload keys are standardized to camelCase (`userId`, `query`) to make downstream processing consistent.
- Logging remains a simple print of JSON to preserve basic existing behaviour.

## How to run tests

Run the test suite with:

```bash
python run_tests
```

`run_tests` will exit with a non-zero status if any tests fail.

## Notes

- No original files were modified; all refactor work is implemented in new files under `refactored/` and `tests/`.
- The public API (class names, constructor args, and `run` return structure) is preserved for compatibility.
