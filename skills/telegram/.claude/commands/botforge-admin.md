---
description: Сгенерировать админ-панель бота (stats, users, broadcasts, settings)
argument-hint: "[inline | webapp | both]"
---

Добавь admin-панель. Формат: $ARGUMENTS (по умолчанию `inline`).

### Inline (в Telegram, без Mini App)

**Структура:**
```
app/handlers/admin/
  __init__.py         # router, include_all, filter = RoleFilter(Role.admin)
  menu.py             # /admin → inline-меню
  stats.py            # Метрики: users, DAU, MAU, revenue
  users.py            # Поиск юзера, ban/unban, grant role
  broadcasts.py       # см. botforge-broadcast
  content.py          # (для Media) управление контентом
  settings.py         # тексты, тарифы (feature flags)
  audit.py            # просмотр audit_events
```

**Inline-меню:**
```python
# app/keyboards/inline/admin.py
def admin_menu_kb() -> K:
    return K(inline_keyboard=[
        [B(text="Статистика", callback_data="adm:stats")],
        [B(text="Пользователи", callback_data="adm:users"),
         B(text="Рассылки", callback_data="adm:bcast")],
        [B(text="Контент", callback_data="adm:content"),
         B(text="Настройки", callback_data="adm:settings")],
        [B(text="Audit", callback_data="adm:audit")],
    ])
```

### WebApp (Mini App админки)

Для сложной админки (таблицы, графики, bulk-ops):

**Backend:**
- `api/routers/admin/*.py` — все защищены `Depends(require_role(Role.admin))`
- Эндпоинты: `GET /admin/stats`, `GET /admin/users?q=&limit=`, `POST /admin/users/{id}/ban`, `GET /admin/broadcasts`, `POST /admin/broadcasts`, `GET /admin/audit?from=&to=`

**Frontend:**
- `webapp/src/pages/admin/` — отдельные страницы
- Роуты активны только если JWT содержит `role=admin`
- React Query / SWR для data fetching
- shadcn/ui или Tailwind UI для таблиц

### Метрики (обязательный минимум)
- Total users, active today / 7d / 30d
- New users today / 7d / 30d (chart)
- Active subscriptions by plan
- Revenue today / 7d / 30d (по провайдерам)
- Top broadcasts by CTR
- Error rate за 24ч

### Audit log
Модель:
```python
audit_events(id, actor_id, action, target_type, target_id,
             payload jsonb, created_at)
```
Каждое admin-действие пишет запись. Примеры actions:
`role.grant`, `role.revoke`, `user.ban`, `user.unban`,
`broadcast.create`, `broadcast.send`, `settings.update`.

### Безопасность
- [ ] Все admin-endpoints за `RoleFilter(Role.admin)` или `require_role(Role.admin)`
- [ ] Аудит-запись ДО выполнения действия (транзакционно)
- [ ] Bulk-операции требуют подтверждения (especially broadcasts и bans)
- [ ] Rate limit на admin-API не мешает работе, но ловит автоматизированные атаки
- [ ] Admin session JWT TTL короче обычного (1–2 ч)

### Tests
- `tests/integration/admin/test_users.py` — ban/unban flow, role grant
- Проверка, что non-admin получает 403
- Проверка, что audit-событие записано
