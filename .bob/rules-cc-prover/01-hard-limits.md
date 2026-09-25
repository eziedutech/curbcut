# CurbCut Prover: Hard Limits

- Write exactly one test per fix. The test must fail before the fix and pass after.
- Never weaken an assertion (e.g., changing >= 4.5 to >= 3.0) to make a test pass.
- Never use pytest.mark.skip, pytest.mark.xfail, or unconditional pass statements.
- Assert on requirements (accessible name present, contrast ratio meets threshold),
  never on implementation details (CSS class name, element tag, attribute value).
- Test files must match the pattern tests/a11y/test_*.py and no other location.
- Do not modify source code or fixture files. Only write test files.
- Run curbcut verify after writing the test to confirm it behaves as expected.
