#!/bin/bash
# Kompilierungs-Script für wissenschaftliche Arbeit

cd "$(dirname "$0")"

echo "======================================================================="
echo "Kompiliere wissenschaftliche Arbeit..."
echo "======================================================================="

# Schritt 1: LaTeX kompilieren
echo ""
echo "[1/4] Erste LaTeX-Kompilierung..."
pdflatex -interaction=nonstopmode hauptarbeit.tex > /dev/null 2>&1

# Schritt 2: BibTeX ausführen
echo "[2/4] BibTeX für Referenzen..."
bibtex hauptarbeit > /dev/null 2>&1

# Schritt 3: LaTeX nochmal kompilieren
echo "[3/4] Zweite LaTeX-Kompilierung..."
pdflatex -interaction=nonstopmode hauptarbeit.tex > /dev/null 2>&1

# Schritt 4: LaTeX nochmal kompilieren (für TOC und Refs)
echo "[4/4] Dritte LaTeX-Kompilierung..."
pdflatex -interaction=nonstopmode hauptarbeit.tex > /dev/null 2>&1

echo ""
echo "======================================================================="

# Prüfe auf Fehler
if pdflatex -interaction=nonstopmode hauptarbeit.tex > hauptarbeit_check.log 2>&1; then
    echo "✓ Kompilierung erfolgreich!"
    echo ""
    echo "Ausgabedatei: hauptarbeit.pdf"
    
    # Räume auf
    rm -f *.aux *.log *.bbl *.blg *.out *.toc *.fls *.fdb_latexmk *.synctex.gz hauptarbeit_check.log
    
else
    echo "✗ Fehler bei der Kompilierung!"
    echo ""
    echo "Fehlerdetails:"
    tail -30 hauptarbeit_check.log
    exit 1
fi

echo "======================================================================="
