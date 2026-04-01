# Suggy Sweep

Десктопный инструмент для подготовки ПК к переустановке Windows: сканирование файлов, AI (Lovable Gateway), экспорт браузеров и приложений, бэкап, восстановление, список установленного ПО и скрипты для переустановки.

## Стек

- **Backend:** Python 3.11+, FastAPI, порт `8765`
- **Frontend:** React 18, TypeScript, Vite (`base: ./` — совместимо с Electron `loadFile`)
- **Desktop:** Electron 30, ожидание API перед открытием окна; сборка через **electron-builder**

## Быстрый старт (разработка)

Из **корня репозитория**:

```bash
pip install -r backend/requirements.txt
npm install
npm install --prefix frontend
npm install --prefix electron
```

Терминал 1 — API:

```bash
python backend/main.py
```

Терминал 2 — UI:

```bash
npm run dev --prefix frontend
```

Откройте в браузере URL Vite (по умолчанию `http://127.0.0.1:5173`).

### Один командой (backend + frontend)

```bash
npm install
npm run dev
```

(нужен `concurrently` из корневых `devDependencies`.)

### Backend + frontend + Electron

```bash
npm run dev:electron
```

Сначала поднимаются Python и Vite, затем **wait-on** ждёт `8765` и `5173`, после чего запускается Electron. Интерпретатор Python: **`py -3`** (Windows) или **`python3`**; переопределение: **`SUGGY_PYTHON`**.

## Переменные окружения

| Переменная | Где | Назначение |
|------------|-----|------------|
| `LOVABLE_API_KEY` | процесс backend | AI через Lovable Gateway |
| `VITE_API_BASE` | сборка frontend | База API, по умолчанию `http://127.0.0.1:8765/api` (см. `frontend/.env.example`) |
| `SUGGY_PYTHON` | Electron | Команда/путь к Python для запуска `backend/main.py` |
| `SUGGY_DEV_SERVER_URL` | Electron (dev) | URL Vite, по умолчанию `http://127.0.0.1:5173` |
| `SUGGY_BACKEND_URL` | Electron | URL проверки готовности API, по умолчанию `http://127.0.0.1:8765/api/system/info` |
| `SUGGY_REMOTE_URL` | `push-github.bat` | URL `origin` (например форк: `https://github.com/ВАШ_ЛОГИН/SuggySweep.git`). По умолчанию — `suggy67/SuggySweep` |

Для AI также поддерживается автоматический токен из `ai.txt`:
- сначала читается локальный `<repo_root>/ai.txt`;
- если файла нет/он пустой — берется `ai.txt` из GitHub raw (`main`, затем `master`);
- токен автоматически перечитывается во время работы (интервал ~12 секунд, и мгновенно при изменении локального файла).

## Сборка установщика (Windows)

1. Установите зависимости frontend и electron (см. выше).
2. Из корня:

```bash
npm run build:desktop
```

Собирается `frontend/dist`, компилируется main-процесс Electron, в `electron/release` появятся **portable** и **NSIS** (нужен установленный Python на целевой машине для backend из `resources/backend`).

### BAT-скрипты (Windows)

- `build-exe.bat` — полный цикл сборки EXE (зависимости + `build:desktop`).
- `push-github.bat` — публикация в `https://github.com/suggy67/SuggySweep`.

Примеры:

```bat
build-exe.bat
```

```bat
push-github.bat "feat: update desktop build and backup flows"
```

> `push-github.bat` по умолчанию **не коммитит `ai.txt`**, чтобы не утек токен.  
> Если изменились **только** `ai.txt`, Git будет пустым — это нормально. Либо коммитьте другие файлы, либо осознанно:  
> `set SUGGY_COMMIT_AI=1` и снова `push-github.bat "сообщение"` (токен попадёт в историю Git).  
> Если коммитов нечего, но они уже есть локально, скрипт попробует **только `git push`**.

### GitHub: `403 Permission denied` при `git push`

Сообщение вида `Permission to suggy67/SuggySweep.git denied to ayvabrat` значит: **Git использует аккаунт `ayvabrat`**, а пуш идёт в репозиторий, куда у этого пользователя **нет прав записи**.

Варианты:

1. Выполнить push под **владельцем** репозитория `suggy67` (войти в Git Credential Manager / выдать PAT с правами на репозиторий).
2. Создать **fork** на GitHub и пушить в свой fork:
   ```bat
   set SUGGY_REMOTE_URL=https://github.com/ВАШ_ЛОГИН/SuggySweep.git
   push-github.bat "feat: sync"
   ```
3. Попросить **добавить ваш аккаунт collaborator** в `suggy67/SuggySweep`.

Сброс сохранённого логина GitHub в Windows (после этого `git push` снова спросит учётные данные):

```bat
cmdkey /delete:git:https://github.com
```

## API (кратко)

- `GET /api/system/info`, `GET /api/drives/list`, `POST /api/drives/check-space`
- `WS /api/scan/ws/scan`, `POST /api/scan/quick-scan`
- `POST /api/ai/*` (SSE)
- `GET /api/browsers/detect`, `POST /api/browsers/export`
- `GET /api/apps/detect`, `POST /api/apps/export`
- `GET /api/programs/list`, **`GET /api/programs/reinstall-script?format=powershell|txt&limit=`** — скачиваемый скрипт / список для переустановки
- `POST /api/backup/create`, `POST /api/backup/preview`, `POST /api/backup/restore`

## Поведение «как надо»

- Frontend берёт базу API из **`VITE_API_BASE`**; WebSocket сканера строится от того же хоста.
- Electron **ждёт ответ backend** перед загрузкой окна; в production открывается **`resources/app/index.html`**, Python запускается из **`resources/backend`** с **`cwd`** = каталог `backend`.
- Список программ можно выгрузить в **PowerShell** (комментарии + подсказки `winget search` + экспорт CSV) или **текстовый список** со страницы «Все программы».
- Добавлены экспортёры **PuTTY** (ветка реестра) и **WinSCP** (ini / папки в AppData и Documents).

Лицензия и публикация — по усмотрению автора проекта.
