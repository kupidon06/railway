# Railway Digital Twin — Цифровой двойник железнодорожного узла

Интеллектуальная платформа для визуализации, симуляции и прогнозирования операций на российских железных дорогах.

---

## Возможности

### Текущий функционал

- **Модели данных**: Node (станции/узлы/депо), Track (пути), Train (поезда), Schedule (расписания), Event (события), Incident (инциденты), TrainPosition (позиции поездов)
- **Сценарии симуляции**: задержки, закрытия путей, перегрузки, инциденты, обслуживание
- **AI/ML**: прогнозирование перегрузок, обнаружение аномалий, прогнозирование задержек
- **Маршрутизация**: A\* по графу OSM, перепланирование при инцидентах
- **RBAC**: ADMIN, OPERATOR, ANALYST, VIEWER, API_USER
- **Аутентификация**: OAuth 2.0 с PKCE через djengoo.com
- **API**: полный REST API с документацией OpenAPI/Swagger/Redoc
- **Интерактивная карта**: OSM + GeoJSON слои
- **SSE**: real-time поток позиций поездов

### Страницы

| Страница        | URL                    | Описание                        |
| --------------- | ---------------------- | ------------------------------- |
| Дашборд         | `/dashboard/`          | KPI, графики, карта             |
| Поезда          | `/trains/`             | список поездов                  |
| Узлы            | `/nodes/`              | станции и пути                  |
| Инциденты       | `/incidents/`          | управление инцидентами          |
| Расписания      | `/schedules/`          | расписания и задержки           |
| Симуляция       | `/simulation/`         | сценарии симуляции              |
| Карта           | `/map/`                | интерактивная карта             |
| Отслеживание    | `/tracking/`           | позиции поездов в реальном времени |
| AI Прогнозы     | `/ai/`                 | список прогнозов, маршрутизация |
| Создать прогноз | `/ai/create/`          | создание прогноза (3 поля)      |

---

## Стек технологий

| Компонент          | Технология                              |
| ------------------ | --------------------------------------- |
| Backend            | Django 5.2.9, DRF 3.15.2               |
| База данных        | PostgreSQL 16 + PostGIS                 |
| Очереди            | Redis, Celery 5.4                       |
| Визуализация       | Martin (Maplibre), MapLibre GL JS       |
| OSM данные         | osm2pgsql, NetworkX, Shapely, GeoPandas |
| Аутентификация     | social-auth-app-django, djengoo.com (PKCE) |
| Документация API   | drf-spectacular (Swagger, Redoc)        |
| Контейнеризация    | Docker, docker-compose                  |
| Туннель            | cloudflared / ngrok                     |
| UI                 | Django Templates + Alpine.js + Chart.js + Tailwind CSS |

---

## Архитектура приложения

```
railway/
├── apps/
│   ├── common/          # Базовые модели (TimeStamped, SoftDelete), RBAC permissions
│   ├── core/            # Ядро: Node, Track, Train, Schedule, Event, Incident
│   ├── twin/            # Цифровой двойник: TrainPosition
│   ├── simulation/      # Симуляция: SimulationScenario, SimulationRun
│   ├── ai/              # AI/ML: MLModel, PredictionResult, IncidentRouter
│   └── analytics/       # Аналитика: Alert, DashboardViewSet
├── djengoo/             # Фронтенд (шаблоны), OAuth2 провайдер
├── conf/                # Настройки Django (base, development, production)
├── docker-compose.yml   # 3 сервиса: web, db, martin
└── Dockerfile           # Python 3.12-slim + GDAL + osm2pgsql
```

### Настройки окружения

- `conf/settings/base.py` — общие настройки
- `conf/settings/development.py` — разработка (DEBUG=True, ALLOWED_HOSTS=\*, CSRF_TRUSTED_ORIGINS=\*)
- `conf/settings/production.py` — продакшен (PostgreSQL, Redis, Celery, HTTPS)

### База данных

Проект использует PostgreSQL с расширением PostGIS для геопространственных данных. OSM данные загружаются через osm2pgsql в таблицы `planet_osm_line/point/polygon`.

---

## Установка и запуск

### Через Docker (рекомендуется)

```bash
# Клонировать репозиторий
cd railway

# Запустить все сервисы
docker compose up --build

# Создать суперпользователя
docker compose exec web python manage.py createsuperuser

# Импортировать данные
docker compose exec web python manage.py seed_data
docker compose exec web python manage.py import_osm          # только если OSM данные загружены
docker compose exec web python manage.py train_models        # обучить модели ML
```

**Доступные сервисы:**
- **Web**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **Swagger**: http://localhost:8000/api/docs/
- **Redoc**: http://localhost:8000/api/redoc/
- **Martin (tiles)**: http://localhost:3000

### Локальная разработка

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настройка PostgreSQL (или используйте SQLite по умолчанию)
export DB_HOST=localhost DB_NAME=railway_db DB_USER=railway_user DB_PASSWORD=railway_pass

python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

---

## Импорт данных

### seed_data — демо-данные

```bash
python manage.py seed_data              # загрузить
python manage.py seed_data --clear      # очистить и загрузить
```

Создаёт:
- **8 станций**: Ленинградский вокзал, Казанский, Киевский, Белорусский, Павелецкий, Курский, Московский (СПб), Нижний Новгород
- **Пути** для каждой станции (на основе capacity)
- **12 поездов**: Aeroexpress, TGV, Intercité, TER, Cargo
- **Расписания** (прошлые, текущие, будущие)
- **40 событий** (прибытия, отправления, задержки)
- **3 инцидента** (отказ сигнализации, обслуживание путей, перегрузка)
- **Позиции поездов**

### import_osm — импорт из OpenStreetMap

```bash
python manage.py import_osm                    # импорт всей Москвы
python manage.py import_osm --clear            # очистить и импортировать
python manage.py import_osm --bbox "37.5,55.6,37.8,55.8"  # по BBOX
```

Импортирует реальный граф из PostGIS OSM таблиц:
- Станции из `planet_osm_point` → `Node (STATION)`
- Пересечения из `planet_osm_line` → `Node (JUNCTION)`
- Разделение OSM way на сегменты → `Track`

### train_models — обучение ML моделей

```bash
python manage.py train_models
python manage.py train_models --clear
```

Создаёт 3 модели на основе данных расписаний:
1. **Congestion Prediction** — анализ плотности расписаний по узлам/часам
2. **Anomaly Detection** — статистическое обнаружение выбросов (Z-Score)
3. **Delay Prediction** — исторический средний анализ задержек

---

## API Endpoints

### Core (`/api/v1/`)

| Метод | Endpoint                  | Описание                  |
| ----- | ------------------------- | ------------------------- |
| GET   | `/nodes/`                 | список узлов              |
| POST  | `/nodes/`                 | создать узел              |
| GET   | `/tracks/`                | список путей              |
| GET   | `/trains/`                | список поездов            |
| GET   | `/schedules/`             | расписания                |
| GET   | `/events/`                | события                   |
| GET   | `/incidents/`             | инциденты                 |
| POST  | `/incidents/{id}/resolve/`| разрешить инцидент        |

### Digital Twin (`/api/v1/twin/`)

| Метод | Endpoint             | Описание                        |
| ----- | -------------------- | ------------------------------- |
| GET   | `/positions/`        | позиции поездов                 |
| GET   | `/positions/latest/` | последняя позиция каждого поезда |

### Simulation (`/api/v1/simulation/`)

| Метод | Endpoint                          | Описание                   |
| ----- | --------------------------------- | -------------------------- |
| GET   | `/scenarios/`                     | список сценариев           |
| POST  | `/scenarios/{id}/clone/`          | клонировать сценарий      |
| POST  | `/scenarios/{id}/run/`            | запустить симуляцию       |
| GET   | `/runs/`                          | результаты запусков       |
| POST  | `/runs/{id}/cancel/`              | отменить запуск           |

### AI/ML (`/api/v1/ai/`)

| Метод | Endpoint                                 | Описание                        |
| ----- | ---------------------------------------- | ------------------------------- |
| GET   | `/models/`                               | список ML моделей               |
| POST  | `/models/{id}/activate/`                 | активировать модель             |
| GET   | `/predictions/`                          | прогнозы                        |
| POST  | `/predictions/create-prediction/`        | создать прогноз                 |
| POST  | `/incident-routing/`                     | анализ инцидента + маршрутизация |

### Analytics (`/api/v1/analytics/`)

| Метод | Endpoint                                          | Описание                      |
| ----- | ------------------------------------------------- | ----------------------------- |
| GET   | `/dashboard/`                                     | KPI дашборда                  |
| GET   | `/dashboard/congestion_by_node/`                   | перегрузка по узлам           |
| GET   | `/dashboard/route/?from=...&to=...`               | маршрут A→B                   |
| GET   | `/dashboard/railways-geojson/`                    | GeoJSON железных дорог        |
| GET   | `/dashboard/delay_distribution/`                  | распределение задержек        |
| GET   | `/alerts/`                                        | список оповещений             |
| POST  | `/alerts/{id}/acknowledge/`                       | подтвердить оповещение        |
| POST  | `/alerts/{id}/dismiss/`                           | отклонить оповещение          |
| GET   | `/alerts/active/`                                 | активные оповещения           |

---

## Система маршрутизации

### RailwayRouter (`apps/core/routing.py`)

- Строит граф из OSM данных PostGIS (`planet_osm_line` → NetworkX Graph)
- A\* поиск кратчайшего пути между двумя координатами
- Интерполяция положения на маршруте по проценту прогресса

### IncidentRouter (`apps/ai/router.py`)

- Находит поезда, затронутые блокировкой узла
- Пытается перемаршрутизировать через альтернативные узлы
- Падает на план DELAY, если объезд невозможен

---

## Симуляция

`SimulationEngine` (`apps/simulation/engine.py`):
1. Определяет затронутые поезда и маршруты
2. Запускает A\* на графе RailwayRouter
3. Создаёт TrainPosition, Schedule, Event записи
4. Вычисляет KPI (затронутые поезда, общая задержка, конфликты)

Типы сценариев: DELAY, CLOSURE, CONGESTION, INCIDENT, MAINTENANCE, CUSTOM

---

## Система AI/ML

### Модели

Три предобученные модели (через `train_models`):
- **Congestion Prediction** — статистический анализ плотности
- **Anomaly Detection** — Z-Score обнаружение выбросов
- **Delay Prediction** — регрессия на исторических данных

### Создание прогноза

Форма на `/ai/create/` содержит поля:
1. **Поезд** — выбор из API `/api/v1/trains/?page_size=5000`
2. **Узел** — выбор из API `/api/v1/nodes/?node_type=STATION&page_size=5000`
3. **Тип проблемы** — CONGESTION / DELAY / INCIDENT / CLOSURE / MAINTENANCE
4. **Модель** — выбор из API `/api/v1/ai/models/`

Backend автоматически генерирует прогноз на основе модели и данных расписания.

### Маршрутизация при инцидентах

`POST /api/v1/ai/incident-routing/` принимает JSON:
```json
{
  "incident_id": "uuid",
  "mode": "fastest"
}
```

Возвращает: затронутые поезда, альтернативные маршруты, конфликты, план действий.

---

## RBAC Permissions

| Роль       | Права                                                         |
| ---------- | ------------------------------------------------------------- |
| **ADMIN**  | полный доступ, управление пользователями, настройки           |
| OPERATOR   | управление узлами, расписаниями, инцидентами, оповещениями, симуляция |
| ANALYST    | просмотр отчётов, симуляция (чтение)                          |
| VIEWER     | дашборд только для чтения                                     |
| API_USER   | программный доступ к API (ингрес данных)                      |

---

## Туннель для внешнего доступа

### Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:8000
```

**Примечание**: WSL может блокировать QUIC/TCP порт 7844. Если соединение не устанавливается, используйте ngrok.

### ngrok

```bash
ngrok http 8000
```

После настройки туннеля URL будет автоматически добавлен в `CSRF_TRUSTED_ORIGINS` (настройка `['http://*', 'https://*']` в development.py разрешает все источники).

---

## Управляющие команды

| Команда               | App     | Описание                              |
| --------------------- | ------- | ------------------------------------- |
| `seed_data`           | core    | генерация демо-данных                 |
| `import_osm`          | core    | импорт графа OSM Москвы              |
| `train_models`        | ai      | обучение 3 ML моделей                |

---

## Разработка

### Линтер/форматтер

```bash
ruff check .           # линтинг
ruff format .          # форматирование
```

### Тесты

```bash
python manage.py test
```

---

## Структура файлов

```
railway/
├── apps/
│   ├── ai/                 # models, viewsets, urls, router, management commands
│   ├── analytics/          # models, viewsets, urls
│   ├── common/             # base models, permissions, mixins, signals
│   ├── core/               # models, viewsets, urls, routing, management commands
│   ├── simulation/         # models, viewsets, urls, engine
│   └── twin/               # models, viewsets, urls
├── conf/
│   ├── settings/           # base.py, development.py, production.py
│   ├── urls.py             # корневая конфигурация URL
│   └── wsgi.py / asgi.py
├── djengoo/
│   ├── templates/djengoo/  # 15 HTML шаблонов (русский язык)
│   ├── views.py            # все view функции
│   ├── urls.py             # маршруты фронтенда
│   ├── backends.py         # OAuth2 бэкенд (djengoo.com)
│   └── stream.py           # SSE поток
├── static/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Статус проекта

- ✅ База данных: PostgreSQL + PostGIS
- ✅ OSM граф: 69 462 линий, 1292 станции, 19 151 узел
- ✅ API: полный REST + OpenAPI документация
- ✅ Фронтенд: 15 страниц на русском языке
- ✅ Симуляция: 6 типов сценариев, A\* маршрутизация
- ✅ AI/ML: 3 обученные модели, прогнозирование, маршрутизация инцидентов
- ✅ Аутентификация: OAuth 2.0 + PKCE
- ✅ RBAC: 5 ролей
- ✅ Туннель: Cloudflare Tunnel / ngrok
