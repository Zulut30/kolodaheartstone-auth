---
description: Generate a beautiful web admin panel (React + Tailwind + shadcn/ui) connected to your bot via API
argument-hint: "[описание фичей: dashboard, users, broadcasts, audit, payments, content, settings]"
---

Generate a production-ready web admin panel for the current Telegram bot.

**Scope:** $ARGUMENTS

The panel is a separate web app (not inline `/admin` bot menu). It:
- Shares backend code with the bot (`app/services/`, `app/repositories/`, `app/models/`)
- Exposes FastAPI endpoints under `api/routers/admin/*`
- Frontend in `webapp/` as React + Vite + TypeScript + Tailwind + shadcn/ui
- Role-based auth via JWT (admin-only routes)
- Real-time updates via Server-Sent Events

**Read the reference first:** `.claude/skills/botforge/references/admin-panel.md` has the full specification including design system, color palette, component patterns, and security checklist.

**Generate:**

### 1. Backend (FastAPI)
- `api/security.py` — JWT with `role` claim, `require_role(Role.admin)` dependency
- `api/routers/auth.py` — `POST /auth/login` (email+password with bcrypt) + `POST /auth/telegram` (Mini App initData → admin JWT if user ∈ ADMIN_IDS)
- `api/routers/admin/stats.py` — `GET /admin/stats` (users, DAU, active subs, revenue 30d)
- `api/routers/admin/users.py` — list with cursor pagination, search, filter, `POST /:id/ban`, `POST /:id/role`
- `api/routers/admin/payments.py` — list + filter + refund
- `api/routers/admin/subscriptions.py` — list + grant/revoke
- `api/routers/admin/broadcasts.py` — composer + scheduler + SSE progress
- `api/routers/admin/content.py` — CRUD with tier gating (for Media bots)
- `api/routers/admin/settings.py` — feature flags, bot texts
- `api/routers/admin/audit.py` — read-only audit log
- `api/events.py` — SSE stream broadcasting events from services
- `api/pagination.py` — cursor helper
- `api/rate_limit.py` — Redis-based, stricter on `/auth/login`

### 2. Frontend (webapp/)
- `webapp/package.json` with: React 19, Vite, TypeScript, Tailwind, TanStack Query + Table, React Router, zustand, react-hook-form + zod, recharts, lucide-react, sonner, date-fns, axios
- `webapp/tailwind.config.ts` — BotForge color palette (see reference)
- `webapp/src/lib/api.ts` — axios wrapper, auto-attach JWT, 401 → redirect to /login
- `webapp/src/lib/auth.ts` — zustand store for JWT + user
- `webapp/src/lib/realtime.ts` — SSE hook, invalidates queries on events
- `webapp/src/components/ui/*` — shadcn/ui components (button, card, dialog, input, select, sheet, table, tabs, toast, badge, dropdown-menu, avatar)
- `webapp/src/components/layout/AppShell.tsx` — sidebar + content area
- `webapp/src/components/charts/StatCard.tsx` — animated counter card
- `webapp/src/components/charts/RevenueChart.tsx` — Recharts LineChart
- `webapp/src/components/features/UserTable.tsx` — TanStack Table with zebra + hover
- `webapp/src/components/features/BroadcastComposer.tsx` — multi-step drawer
- `webapp/src/components/features/AuditLogViewer.tsx`
- `webapp/src/pages/*` — Dashboard, Login, Users, UserDetail, Subscriptions, Payments, Broadcasts, Content, AuditLog, Settings
- `webapp/src/router.tsx` — route definitions, lazy-loaded non-dashboard pages

### 3. Design system (non-negotiable)
- Dark theme by default, Telegram cyan accent `#2aabee`
- Inter font (display headings 800/900 weight, tight letter-spacing)
- JetBrains Mono for IDs, tokens, code
- Card radius 14–18px, border opacity 40–60%
- Hover: 150ms ease-out with 1px lift + border-color transition to accent
- Empty states: Lucide icon + heading + action button
- Loading: skeleton pulse on cards
- Stat cards: count-up animation on first render (rAF-driven, 600ms ease-out-cubic)

### 4. Infrastructure
- `docker/Dockerfile.api` — FastAPI service (multi-stage, non-root)
- `webapp/Dockerfile` — Vite build → nginx static
- `webapp/nginx.conf` — proxies `/api/*` to api service, SPA fallback
- Add `api` and `webapp` services to `docker-compose.yml`
- Update `.env.example` with `JWT_SECRET`, `ADMIN_IDS`

### 5. Pages to include (mandatory)
- **Dashboard** — 4 stat cards (users, DAU, active subs, revenue 30d) + revenue chart + recent payments table + bot health panel
- **Users** — search + filter + sort, bulk actions, detail page with tabs (Profile / Subscriptions / Payments / Activity / Audit)
- **Broadcasts** — history + multi-step composer drawer (text → segment → preview → confirm) with live progress via SSE
- **Payments** — list + filter + refund + reconciliation CSV export
- **Audit log** — filterable, read-only, paginated

### 6. Security
Apply the security checklist from `admin-panel.md`:
- Admin JWT TTL ≤ 12h
- `require_role(Role.admin)` on every admin endpoint
- CORS whitelist (no `*`)
- Rate limit on `/auth/login`: 5/min/IP
- 2FA for admin accounts (TOTP)
- All admin actions → `audit_events`
- Bulk destructive actions require typed confirmation

### 7. Self-review
- [ ] All admin endpoints guarded by `require_role`
- [ ] SSE endpoint requires auth (token via query param or header)
- [ ] Cursor pagination on all list endpoints (no offset on >10k rows)
- [ ] No admin action executes without `audit_events` record
- [ ] shadcn/ui components in `src/components/ui/` (copied, not npm)
- [ ] Tailwind config matches BotForge palette (`#2aabee` accent, dark default)
- [ ] Frontend bundle ≤ 250 KB initial
- [ ] Real-time updates don't leak cross-user data in SSE
- [ ] Frontend builds (`npm run build`) + backend starts (`uvicorn api.main:app`)
- [ ] `docker-compose up` brings up bot + postgres + redis + api + webapp, all healthy

### 8. Deploy note
After generation, run:
```bash
cd webapp
pnpm install
pnpm dlx shadcn@latest init  # configure with the palette in tailwind.config.ts
pnpm dlx shadcn@latest add button card dialog input select sheet table tabs toast badge dropdown-menu avatar
pnpm run build
cd ..
docker compose up -d --build
```

The panel will be live at `http://localhost:5173` (dev) or behind your domain (prod).
