# CLAUDE.md — drom.mn

Монгольский автомобильный маркетплейс (аналог Drom.ru). Таргет — Улан-Батор.
Единый SaaS-продукт, **без per-client кастомизаций**. Язык интерфейса по
умолчанию — монгольский, таймзона `Asia/Ulaanbaatar`.

Стек: **Django 5 + DRF (backend) / React 18 + TypeScript + Vite (frontend) /
PostgreSQL 16**. Всё крутится в Docker.

---

## Как читать этот файл

Этот файл — правила для агента (Claude Code) при работе над проектом.
Архитектуру здесь определяет **ведущий разработчик**. Не выдумывай новые
подходы — повторяй существующие паттерны, описанные ниже. Если задача требует
выйти за рамки этих паттернов — **остановись и спроси** (см. «Защищённые зоны»).

---

## Запуск и проверка

```bash
docker-compose up            # поднять всё: postgres + backend + frontend + nginx
                             # приложение → http://localhost:8082
```

Внутри контейнера backend:
```bash
python manage.py migrate                 # применить миграции
python manage.py seed                    # минимальный каталог + тестовые данные
python manage.py test                    # ВСЕ тесты Django
python manage.py test listings           # тесты одного приложения
```

Frontend:
```bash
npm run dev        # дев-сервер Vite на :5173 (проксирует /api на :8000)
npm run build      # tsc (проверка типов) + vite build — ОБЯЗАТЕЛЬНО прогонять
                   # перед тем как считать фронтовую задачу готовой
```

> ⚠️ Сейчас в проекте **почти нет тестов** (один smoke-тест в
> `backend/listings/tests/`) и **не настроены линтеры**. Это известная дыра.
> Для нового кода — пиши тесты рядом с существующим smoke-тестом и прогоняй
> `npm run build` для типов на фронте. Не считай задачу готовой без этого.

---

## Архитектура backend (`backend/`)

Django-проект `config/`. Приложения = домены. **Не создавай новые приложения
без подтверждения.**

| Приложение | Зона ответственности | Ключевые модели |
|---|---|---|
| `core` | Абстрактные миксины, курс валют, health | `LocalizedNameMixin`, `SlugMixin`, `ExchangeRate` |
| `users` | Кастомная авторизация по телефону, профили продавцов | `User` (AUTH_USER_MODEL), `SellerProfile` |
| `vehicles` | Каталог авто: марки→модели→поколения→комплектации | `Brand`, `Model`, `Generation`, `Trim` |
| `references` | Канонические справочники | `BodyType`, `Color`, `FuelType`, `TransmissionType`, `DriveType`, `Country` |
| `geo` | География Монголии, поиск по радиусу | `Region`, `City` |
| `listings` | Объявления, фильтры, избранное, аналитика | `Listing`, `ListingPhoto`, `ListingPriceHistory`, `UserFavorite`, `ListingView` |

### Дерево каталога (важно)
```
Brand → Model → Generation → Trim
```
Объявление (`Listing`) ссылается на любой уровень этого дерева + на канонические
справочники. Целостность дерева проверяется `validate_vehicle_tree()` —
используй её, не дублируй логику.

### Паттерны backend — ОБЯЗАТЕЛЬНЫ к повторению

- **Сервисный слой.** Бизнес-логика живёт в `<app>/services.py`, НЕ во вьюхах
  и НЕ в сериализаторах. Примеры: `listings/services.py`
  (`create_listing`, `update_listing`, `search_listings`, `record_listing_view`),
  `users/services.py` (`register_user`), `core/services.py` (курс валют).
  Вьюха = тонкая, дёргает сервис.
- **Фильтрация** — через django-filter в `listings/filters.py`. Поддерживает
  мультивыбор через запятую (`body_type=1,2,3`) и проверяет значение и на самом
  Listing, и на унаследованном от Trim. Новые фильтры добавляй туда же тем же
  стилем.
- **Канонические справочники.** Значения body_type/fuel/transmission/drive
  валидируются против канонического списка (`references/body_types.py`,
  `references/vehicle_refs.py`). Нельзя писать в Listing произвольный справочник —
  только канонический. `ListingWriteSerializer` это уже проверяет.
- **API:** DRF, JWT (`djangorestframework-simplejwt`), по умолчанию
  `IsAuthenticatedOrReadOnly`, пагинация 20/страницу. Роуты — в `config/urls.py`
  и `<app>/urls.py`.
- **Сериализаторы listings** разделены: `ListingListSerializer` (список),
  `ListingDetailSerializer` (деталь), `ListingWriteSerializer` (запись). Не
  сваливай всё в один.

---

## Архитектура frontend (`frontend/`)

Vite + React 18 + **TypeScript (strict)**. Менеджер пакетов — **npm**.

```
src/
  api/        — слой запросов к backend (fetch-обёртка client.ts, токены в localStorage)
  components/ — layout/ (шапка, хлебные крошки), listings/, ui/ (переиспользуемое)
  pages/      — страницы под роуты (CatalogPage, ListingDetailPage, Sell*, Login/Register)
  store/      — состояние (СВОЙ store на useSyncExternalStore, createStore.ts)
  lib/        — утилиты, i18n, форматирование, пресеты фильтров
  types.ts    — общие TS-типы
  index.css   — ВСЕ стили (плоский CSS, BEM-подобные классы)
```

### Паттерны frontend — ОБЯЗАТЕЛЬНЫ к повторению

- **Состояние — свой лёгкий store** через `store/createStore.ts`
  (`authStore`, `catalogStore`, `refsStore`, `listingDetailStore`).
  **НЕ добавляй Redux / Zustand / react-query** — используй этот паттерн.
- **Запросы — нативный `fetch`** через обёртку `api/client.ts` (она кладёт
  Bearer-токен, разбирает ошибки бэка). **НЕ добавляй axios.** Новые эндпоинты
  оформляй файлом в `api/` по образцу `listings.ts` / `references.ts`.
- **Стили — плоский CSS** в `index.css`, классы в стиле `.listing-card`,
  `.catalog-page`. **НЕ добавляй Tailwind / styled-components / CSS-in-JS / MUI.**
- **Роутинг** — react-router-dom v6 в `App.tsx`. Каталог использует
  ЧПУ-роуты `/:brandSlug/:modelSlug/:generationSlug`.
- **i18n** — 3 языка (mn/ru/en), ключи в `lib/labels.ts`, локаль в localStorage.
  Любой пользовательский текст — через i18n, не хардкодь строки.
- **Типы** — strict TS. `npm run build` обязан проходить без ошибок типов.

---

## Защищённые зоны — СПРОСИ ЧЕЛОВЕКА, не действуй сам

Эти действия требуют **явного подтверждения человека** (не «джун попросил» —
именно подтверждение). Если уверенности нет — остановись и спроси.

1. **Миграции БД.** Любое изменение схемы (`makemigrations`/`migrate`,
   новое поле, изменение модели) — сначала скажи: *«это изменит схему БД,
   подтверди»* и дождись ответа. Backend в Docker гоняет `migrate` на старте —
   кривая миграция уедет сразу.
2. **Новая архитектурная сущность** — новое Django-приложение, новый внешний
   сервис, новая зависимость (`requirements.txt` / `package.json`), новый
   паттерн состояния/запросов/стилей. Это решение ведущего разработчика.
   Скажи: *«это выходит за рамки задачи, нужно решение ведущего разработчика»*.
3. **Удаление или массовое изменение данных** (миграции данных, bulk update/delete,
   management-команды, трогающие много строк) — обязательное явное подтверждение.
4. **Секреты.** `.env`, `DJANGO_SECRET_KEY`, токены, пароли БД — никогда не
   коммитить, не логировать, не выводить в ответах. `.env.example` — только
   с плейсхолдерами.
5. **Деплой.** Не «деплой» без прохождения тестов. (Полноценного
   prod/staging-деплоя пока нет — см. дыры выше; реальный деплой согласуй.)

---

## Команды и парсер каталога

- Импорт каталога с drom.ru: `python manage.py import_drom` (+ `--dry-run`,
  `--brand`, `--no-photos`). Парсер-сырьё — в `scripts/drom_parser/`.
- Прочее: `seed`, `seed_listings`, `fetch_brand_icons`,
  `backfill_generation_info`, `check_references`, `cleanup_body_types`,
  `cleanup_vehicle_refs`.

Эти команды трогают много данных — подпадают под «защищённые зоны», п.3.

---

## Рабочий цикл задачи

1. Принять описание задачи в свободной форме.
2. Если описание неполное/неоднозначное — **задать уточняющие вопросы
   с конкретными вариантами**. Не угадывать бизнес-логику.
3. Писать код строго по паттернам выше. Не плодить новые подходы.
4. Написать/обновить тесты на новый код.
5. Прогнать тесты (`python manage.py test`) и сборку типов (`npm run build`)
   ПЕРЕД тем как считать задачу готовой.
6. Если задача задела защищённую зону — остановиться и спросить.
7. После готовности — короткий отчёт: что сделано и как это проверить
   руками (предполагай, что заказчик код не читает).
