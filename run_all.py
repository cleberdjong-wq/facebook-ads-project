"""
run_all.py
Executa os scripts 01-07 em sequência e abre o dashboard.html no navegador.

Uso: python run_all.py
"""

import subprocess
import sys
import os
from pathlib import Path

BASE = Path(__file__).parent
PYTHON = sys.executable

SCRIPTS = [
    ("01_campanhas.py",      "Campanhas"),
    ("02_cpv_diario.py",     "CPV Diario"),
    ("03_posicionamentos.py","Posicionamentos"),
    ("04_idade_genero.py",   "Idade x Genero"),
    ("05_horarios.py",       "Horarios"),
    ("06_funil.py",          "Funil"),
    ("07_dashboard.py",      "Dashboard"),
]

def run(script, label):
    print(f"\n{'='*60}")
    print(f"  [{label}] Executando {script}...")
    print(f"{'='*60}")
    result = subprocess.run([PYTHON, BASE / script], check=False)
    if result.returncode != 0:
        print(f"[ERRO] {script} falhou (codigo {result.returncode}). Continuando...")
        return False
    return True

def main():
    print("Facebook Ads — Pipeline completo")
    print(f"Diretorio: {BASE}\n")

    ok = 0
    for script, label in SCRIPTS:
        if run(script, label):
            ok += 1

    dashboard = BASE / "dashboard.html"
    print(f"\n{'='*60}")
    print(f"  Concluido: {ok}/{len(SCRIPTS)} scripts com sucesso")
    print(f"{'='*60}")

    if dashboard.exists():
        print(f"\nAbrindo {dashboard.name}...")
        os.startfile(str(dashboard))
    else:
        print("\n[AVISO] dashboard.html nao foi gerado.")

if __name__ == "__main__":
    main()
