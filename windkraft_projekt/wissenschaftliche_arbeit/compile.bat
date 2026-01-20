@echo off
REM Kompilierungs-Script für wissenschaftliche Arbeit (Windows)

echo ============================================================================
echo Kompiliere wissenschaftliche Arbeit...
echo ============================================================================

cd /d "%~dp0"

echo.
echo [1/4] Erste LaTeX-Kompilierung...
pdflatex -interaction=nonstopmode hauptarbeit.tex > nul 2>&1

echo [2/4] BibTeX für Referenzen...
bibtex hauptarbeit > nul 2>&1

echo [3/4] Zweite LaTeX-Kompilierung...
pdflatex -interaction=nonstopmode hauptarbeit.tex > nul 2>&1

echo [4/4] Dritte LaTeX-Kompilierung...
pdflatex -interaction=nonstopmode hauptarbeit.tex > nul 2>&1

echo.
echo ============================================================================

REM Prüfe auf Fehler
pdflatex -interaction=nonstopmode hauptarbeit.tex > hauptarbeit_check.log 2>&1

if %ERRORLEVEL% equ 0 (
    echo ✓ Kompilierung erfolgreich!
    echo.
    echo Ausgabedatei: hauptarbeit.pdf
    
    REM Räume auf
    del /q *.aux *.log *.bbl *.blg *.out *.toc *.fls *.fdb_latexmk *.synctex.gz 2>nul
    del /q hauptarbeit_check.log 2>nul
    
) else (
    echo ✗ Fehler bei der Kompilierung!
    echo.
    echo Fehlerdetails (letzte 30 Zeilen):
    for /f "skip=1 tokens=*" %%a in ('type hauptarbeit_check.log ^| find /c /v ""') do set lines=%%a
    setlocal enabledelayedexpansion
    set /a skip=!lines!-30
    if !skip! ltr 0 set skip=0
    echo Zeigen letzte 30 Zeilen...
    
    exit /b 1
)

echo ============================================================================
