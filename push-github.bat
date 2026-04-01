@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

echo ==========================================
echo Suggy Sweep - Публикация в GitHub
echo ==========================================

set "ROOT=%~dp0"
set "BRANCH=main"
set "DEFAULT_REMOTE=https://github.com/suggy67/SuggySweep.git"
set "REMOTE_URL=!DEFAULT_REMOTE!"

if defined SUGGY_REMOTE_URL (
  set "RU=!SUGGY_REMOTE_URL!"
  if not "!RU!"=="" (
    set "REMOTE_URL=!RU!"
    echo [INFO] Remote из SUGGY_REMOTE_URL: !REMOTE_URL!
  ) else (
    echo [WARN] SUGGY_REMOTE_URL задан, но пустой — использую по умолчанию: !DEFAULT_REMOTE!
  )
) else (
  echo [INFO] Remote по умолчанию: !REMOTE_URL!
  echo [HINT] Свой форк/другой URL:  set SUGGY_REMOTE_URL=https://github.com/ВАШ_ЛОГИН/SuggySweep.git
)

if "!REMOTE_URL!"=="" (
  echo [ERROR] REMOTE_URL пустой. Удалите пустую переменную SUGGY_REMOTE_URL из среды Windows или задайте корректный URL.
  exit /b 1
)

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
  git remote add origin "!REMOTE_URL!"
) else (
  echo [INFO] Обновляю origin...
  git remote set-url origin "!REMOTE_URL!"
)
echo [INFO] Текущий origin:
git remote -v

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
if errorlevel 1 goto PUSH_FAIL
echo [OK] Push выполнен.
call :OpenGitHub
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
if errorlevel 1 goto PUSH_FAIL

echo [OK] Публикация завершена.
call :OpenGitHub
popd
exit /b 0

:OpenGitHub
if /i "!SUGGY_OPEN_BROWSER!"=="0" exit /b 0
set "GH_PAGE=!REMOTE_URL!"
set "GH_PAGE=!GH_PAGE:.git=!"
echo [INFO] Открываю страницу репозитория в браузере...
start "" "!GH_PAGE!"
exit /b 0

:PUSH_FAIL
echo.
echo [ERROR] git push не удался.
echo.
echo Если ошибка "Repository not found" ^(репозиторий не найден^):
echo   - Чаще всего репозитория ещё НЕТ на GitHub. Создайте его: github.com → New repository,
echo     имя как в URL ^(например SuggySweep^), без README если уже есть локальные коммиты.
echo   - Либо вы пушите не в тот аккаунт: войдите на GitHub под владельцем этого URL и повторите.
echo.
echo Если ошибка 403 / Permission denied:
echo   - У вас в GitHub сейчас залогинен пользователь, у которого НЕТ прав на этот репозиторий.
echo   - Пример: "denied to ayvabrat" — пуш идёт в чужой/организационный репозиторий от другого аккаунта.
echo.
echo Решения:
echo   1^) Войти в GitHub под владельцем репозитория ^(suggy67^) и повторить push.
echo   2^) Сделать fork на GitHub и выставить:
echo        set SUGGY_REMOTE_URL=https://github.com/ВАШ_ЛОГИН/SuggySweep.git
echo      затем снова push-github.bat
echo   3^) Добавить ваш аккаунт как Collaborator в репозитории suggy67/SuggySweep.
echo.
echo Сброс сохранённых учётных данных GitHub ^(Windows^):
echo   cmdkey /list:git:https://github.com
echo   cmdkey /delete:git:https://github.com
echo   затем снова git push — введите PAT или войдите через браузер.
echo.
popd
exit /b 1
