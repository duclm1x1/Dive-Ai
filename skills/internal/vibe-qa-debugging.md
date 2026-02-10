# QA & Debugging

## Khi nhận task bugfix

1. **Repro**: mô tả bước tái hiện + input.
2. **Hypothesis**: 2-3 giả thuyết nguyên nhân.
3. **Instrument**: thêm log/trace tối thiểu.
4. **Fix**: patch nhỏ.
5. **Test**:
   - Unit test cho root-cause.
   - Regression test cho edge cases.
6. **Gate**: lint + test + build.

## Unit test defaults

- Python: pytest + parametrize; avoid heavy I/O.
- JS/TS: jest/vitest tùy repo; mocking boundary.

## Anti-pattern

- Swallow exception.
- Fix “by coincidence” không có test.
