# Super-Coder Skills (Clean Code / SOLID / DRY)

## Output rules

Khi Agent viết code, mặc định tuân thủ:

- **Clean Code**: tên biến/hàm rõ, hạn chế side effects, guard clauses.
- **SOLID**:
  - S: function/class 1 trách nhiệm.
  - O: mở rộng bằng interface/strategy, tránh sửa code cũ.
  - L: thay thế subtype không phá contract.
  - I: interface nhỏ.
  - D: inject dependencies, không hardcode.
- **DRY**: không copy-paste; dùng abstraction hợp lý.

## Checklist trước khi output

- [ ] Có type hints (Python) / types (TS).
- [ ] Có unit tests cho logic chính.
- [ ] Không swallow exception.
- [ ] Không dùng eval/exec.
- [ ] Không có hardcoded secret.
- [ ] Có docs cho API public.

## Patch style

- Diff nhỏ, mỗi PR 1 mục tiêu.
- Đặt tên commit theo Conventional Commits (nếu dùng).
