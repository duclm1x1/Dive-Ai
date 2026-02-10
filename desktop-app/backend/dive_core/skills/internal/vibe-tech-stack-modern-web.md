# Tech-Stack Specifics: Modern Web (React/Next.js, Node/NestJS, Tailwind)

## Next.js / React

- Ưu tiên **server components** (nếu Next 13+), hạn chế client-only.
- Validate data ở boundary (API route / server action).
- Không log secret ra client.
- Có **loading/error boundaries**.

## NestJS

- Chia module rõ: Controller / Service / Module.
- DTO + validation (class-validator) ở edge.
- Inject repository/service, không new trực tiếp.
- Chuẩn hoá exception filter.

## Tailwind

- Dùng design tokens / config theme.
- Tránh class quá dài: extract component, dùng cva/clsx.
- Accessibility: focus styles, aria.

## Gates khuyến nghị

- `npm run lint`
- `npm test`
- `npm run build`
