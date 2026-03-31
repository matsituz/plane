# Mars PM — Plane Fork for Mars IT School

Форк [Plane](https://github.com/makeplane/plane) (open-source project management) с интеграцией Mars ID SSO и Mars-брендингом.

## Upstream

- **Upstream**: `https://github.com/makeplane/plane`
- **Fork**: `https://github.com/matsituz/plane`
- **Branch**: `preview`
- **URL**: `https://plane.marshub.uz`

## Наши изменения (поверх upstream)

### 1. Mars ID SSO (backend)

Прозрачная аутентификация через Mars ID JWT cookie (`__mars_id`).

| Файл | Назначение |
|------|------------|
| `apps/api/plane/authentication/provider/credentials/mars_id.py` | MarsIdProvider — верификация JWT, создание/поиск пользователя |
| `apps/api/plane/authentication/middleware/mars_id.py` | MarsIdAutoLoginMiddleware — автологин при наличии cookie |
| `apps/api/plane/authentication/views/app/mars_id.py` | `/auth/mars-id/` — явный endpoint для логина |
| `apps/api/plane/authentication/urls.py` | Регистрация маршрута |
| `apps/api/plane/authentication/views/__init__.py` | Экспорт MarsIdAuthEndpoint |
| `apps/api/plane/settings/common.py` | Middleware в MIDDLEWARE list |

**Как работает:**
1. Пользователь заходит на `plane.marshub.uz`
2. Middleware проверяет cookie `__mars_id` (домен `.marshub.uz`)
3. JWT (HS256) верифицируется через `MARS_ID_SECRET`
4. Пользователь создаётся/находится по email `{handle}@marshub.uz`
5. Django session создаётся автоматически

**Env var:** `MARS_ID_SECRET` — тот же ключ что `AUTH_SECRET` в Mars ID.

### 2. Mars ID кнопка (frontend)

| Файл | Назначение |
|------|------------|
| `apps/web/core/hooks/oauth/extended.tsx` | Кнопка "Sign in with Mars ID" → `/auth/mars-id/` |

### 3. Mars-брендинг (frontend)

| Файл | Что изменено |
|------|-------------|
| `packages/constants/src/metadata.ts` | SITE_NAME, SITE_TITLE → "Mars PM" |
| `apps/web/core/components/auth-screens/header.tsx` | Mars PM лого на auth-страницах |
| `apps/web/core/components/icons/mars-lockup.tsx` | Компонент Mars PM лого |
| `apps/web/ce/components/navigations/top-navigation-root.tsx` | Убран "Star us on GitHub" |
| `apps/web/ce/components/workspace/edition-badge.tsx` | "Community" → "Mars PM" badge |

## Деплой

### Сервер: `core.marsit.uz`

```
~/plane/
├── repo/              # git clone этого форка
└── deploy/
    ├── docker-compose.yml          # из upstream (не менять)
    ├── docker-compose.override.yml # наши образы
    └── plane.env                   # конфигурация
```

### Docker-образы

| Образ | Источник |
|-------|----------|
| `marsit/plane-backend:latest` | Собираем из `apps/api/Dockerfile.api` |
| `marsit/plane-frontend:latest` | Собираем из `apps/web/Dockerfile.web` |
| Остальные (proxy, space, admin, live, infra) | Официальные `artifacts.plane.so/makeplane/*:stable` |

### Пересборка и деплой

```bash
ssh mars@core.marsit.uz

# 1. Обновить код
cd ~/plane/repo && git pull origin preview

# 2. Пересобрать backend (если менялся apps/api/)
docker build -t marsit/plane-backend:latest -f apps/api/Dockerfile.api apps/api/

# 3. Пересобрать frontend (если менялся apps/web/ или packages/)
docker build -t marsit/plane-frontend:latest -f apps/web/Dockerfile.web .

# 4. Перезапустить
cd ~/plane/deploy
docker compose --env-file plane.env up -d
```

### Порты

| Порт | Сервис |
|------|--------|
| 3080 | Plane proxy (Caddy внутри Docker) |
| 3443 | Plane proxy HTTPS (не используется, TLS на хостовом Caddy) |

### Caddy

`plane.marshub.uz` находится внутри wildcard-блока `*.marshub.uz` (on-demand TLS):

```caddy
@plane host plane.marshub.uz
handle @plane {
    reverse_proxy localhost:3080
}
```

**ВАЖНО:** НЕ создавать отдельный site block для `*.marshub.uz` субдоменов — это ломает TLS.

## Merge upstream обновлений

```bash
cd ~/mars/plane-fork
git remote add upstream https://github.com/makeplane/plane.git  # один раз
git fetch upstream preview
git merge upstream/preview
# Resolve conflicts (наши файлы изолированы, конфликтов минимум)
git push origin preview
```

Наши изменения локализованы в отдельных файлах — конфликты при merge маловероятны.

## Mars ID JWT payload

```json
{
  "sub": "uuid",
  "name": "Имя Фамилия",
  "handle": "username",
  "role": "admin|mentor|student",
  "tg": 123456789,
  "email": "username@marshub.uz",
  "exp": 1234567890
}
```

Поле `email` добавлено нами в `mars-id/server.js:101`.
