# Vibe Advanced Searching (v13.0)

Mục tiêu: Cung cấp khả năng tìm kiếm và định vị file/logic trong repo dựa trên các thuộc tính (facets) như imports, classes, exports.

## Capabilities
- **Facet-based Indexing**: Index repo dựa trên cấu trúc code (AST) thay vì chỉ text đơn thuần.
- **Fast Location**: Tìm kiếm file cực nhanh dựa trên query và metadata.
- **Pointer Registry**: Theo dõi các "hotspots" trong code để ưu tiên khi review.

## Usage
```bash
vibe v13-search index
vibe v13-search locate --query "AuthService"
```

## Best Practices
- Chạy `index` sau mỗi lần thay đổi lớn về cấu trúc repo.
- Sử dụng `locate` để nhanh chóng tìm ra các file bị ảnh hưởng khi refactor.
- Kết hợp với `dependency_graph` để hiểu rõ impact của thay đổi.
