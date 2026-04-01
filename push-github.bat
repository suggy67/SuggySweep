@echo off
setlocal EnableExtensions
chcp 65001 >nul

echo ==========================================
echo Suggy Sweep - Публикация в GitHub
echo Репозиторий: https://github.com/suggy67/SuggySweep
echo ==========================================

set "ROOT=%~dp0"
set "REMOTE_URL=https://github.com/suggy67/SuggySweep.git"
set "BRANCH=main"

pushd "%ROOT%" || (
  echo [ERROR] Не удалось перейти в корень проекта.
  exit /b 1
)

where git >nul 2>&1 || (
  echo [ERROR] git не найден. Установите Git for Windows.
  popd
  exit /b 1
)

if not exist ".git" (
  echo [INFO] Инициализация git репозитория...
  git init
  if errorlevel 1 (
    echo [ERROR] git init завершился с ошибкой.
    popd
    exit /b 1
  )
)

for /f "usebackq delims=" %%r in (`git remote`) do (
  if /i "%%r"=="origin" set "HAS_ORIGIN=1"
)

if not defined HAS_ORIGIN (
  echo [INFO] Добавляю remote origin...
  git remote add origin "%REMOTE_URL%"
) else (
  echo [INFO] Обновляю origin...
  git remote set-url origin "%REMOTE_URL%"
)

echo [INFO] Добавляю изменения...
git add .
if errorlevel 1 (
  echo [ERROR] git add завершился с ошибкой.
  popd
  exit /b 1
)

if exist "ai.txt" (
  if /i "%SUGGY_COMMIT_AI%"=="1" (
    echo [WARN] SUGGY_COMMIT_AI=1 — ai.txt будет включён в коммит ^(токен попадёт в историю Git^).
  ) else (
    echo [WARN] Файл ai.txt найден — по умолчанию НЕ коммитим ^(защита токена^).
    echo [HINT] Чтобы закоммитить ai.txt:  set SUGGY_COMMIT_AI=1  и запустите скрипт снова.
    git reset "ai.txt" >nul 2>&1
    git restore --staged "ai.txt" 2>nul
  )
)

git diff --cached --quiet
if errorlevel 1 goto DO_COMMIT

echo.
echo [INFO] Нечего коммитить в индексе ^(возможно, изменён только ai.txt — см. выше^).
git status -sb
echo.

git rev-parse --verify HEAD >nul 2>&1
if errorlevel 1 (
  echo [WARN] В репозитории ещё нет ни одного коммита.
  echo [HINT] Сделайте правки в файлах проекта ^(не только ai.txt^) или установите SUGGY_COMMIT_AI=1.
  popd
  exit /b 2
)

echo [INFO] Пробую отправить уже существующие коммиты ^(git push^)...
git branch -M %BRANCH%
git push -u origin %BRANCH%
if errorlevel 1 (
  echo [ERROR] git push завершился с ошибкой.
  echo [HINT] Проверьте авторизацию GitHub ^(PAT / Git Credential Manager^).
  popd
  exit /b 1
)
echo [OK] Push выполнен.
popd
exit /b 0

:DO_COMMIT
set "MSG=chore: update Suggy Sweep project"
if not "%~1"=="" set "MSG=%~1"

echo [INFO] Коммит: %MSG%
git commit -m "%MSG%"
if errorlevel 1 (
  echo [ERROR] git commit завершился с ошибкой.
  popd
  exit /b 1
)

echo [INFO] Отправка в origin/%BRANCH%...
git branch -M %BRANCH%
git push -u origin %BRANCH%
if errorlevel 1 (
  echo [ERROR] git push завершился с ошибкой.
  echo [HINT] Проверьте авторизацию GitHub ^(PAT / Git Credential Manager^).
  popd
  exit /b 1
)

echo [OK] Публикация завершена.
popd
exit /b 0
