# HireFit AI - System & Framework Rules

## UI Components
- All UI components MUST be built exclusively using standard `shadcn/ui` components (`Card`, `Input`, `Textarea`, `Button`, `Progress`, `Badge`, `Tabs`, `Label`, `Skeleton`, `Alert`, `Separator`, `ScrollArea`, `Sonner toast`).
- Never use raw `<button>` elements. All buttons, selectable options, and actions must use the shadcn `<Button>` component.

## API Performance
- The `/answer` route must execute with low latency by processing evaluation and next question generation concurrently using `asyncio.gather`.
