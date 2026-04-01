@echo off
setlocal
chcp 65001 >nul

echo ==========================================
echo Suggy Sweep - Сборка EXE
echo ==========================================

set "ROOT=%~dp0"
pushd "%ROOT%" || (
  echo [ERROR] Не удалось перейти в корень проекта.
  exit /b 1
)

where npm >nul 2>&1 || (
  echo [ERROR] npm не найден. Установите Node.js LTS.
  popd
  exit /b 1
)

where python >nul 2>&1 || where py >nul 2>&1 || (
  echo [ERROR] Python не найден. Установите Python 3.11+.
  popd
  exit /b 1
)

echo [1/5] Установка backend зависимостей...
if exist "backend\requirements.txt" (
  python -m pip install -r "backend\requirements.txt"
  if errorlevel 1 (
    echo [ERROR] Не удалось установить Python зависимости.
    popd
    exit /b 1
  )
)

echo [2/5] Установка root зависимостей...
call npm install
if errorlevel 1 (
  echo [ERROR] npm install (root) завершился с ошибкой.
  popd
  exit /b 1
)

echo [3/5] Установка frontend/electron зависимостей...
call npm install --prefix frontend
if errorlevel 1 (
  echo [ERROR] npm install --prefix frontend завершился с ошибкой.
  popd
  exit /b 1
)
call npm install --prefix electron
if errorlevel 1 (
  echo [ERROR] npm install --prefix electron завершился с ошибкой.
  popd
  exit /b 1
)

echo [4/5] Сборка desktop...
call npm run build:desktop
if errorlevel 1 (
  echo [ERROR] npm run build:desktop завершился с ошибкой.
  popd
  exit /b 1
)

echo [5/5] Готово.
echo Артефакты: electron\release\

popd
exit /b 0

