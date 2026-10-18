@echo off
echo ==============================================
echo   Compilando Dopamine Bomber a .EXE
echo ==============================================
echo.
uv run pyinstaller DopamineBomber.spec --noconfirm
echo.
if %ERRORLEVEL% EQU 0 (
    echo ==============================================
    echo   [EXITO] Ejecutable generado correctamente:
    echo   dist\DopamineBomber.exe
    echo ==============================================
) else (
    echo [ERROR] Ocurrio un fallo durante la compilacion.
)
echo.
pause
