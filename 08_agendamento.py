"""
08_agendamento.py
Agendamento automático do pipeline Facebook Ads.

Modos de uso:
  python 08_agendamento.py            → loop contínuo (mantém terminal aberto)
  python 08_agendamento.py --instalar → registra no Agendador de Tarefas do Windows
  python 08_agendamento.py --remover  → remove do Agendador de Tarefas do Windows
  python 08_agendamento.py --status   → exibe próximas execuções e log recente

Log: agendamento.log
"""

import subprocess
import sys
import os
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────

# Horário de execução diária (formato HH:MM)
HORARIO_DIARIO = "08:00"

# Intervalo em horas para modo contínuo (alternativo ao horário fixo)
INTERVALO_HORAS = 24

# Nome da tarefa no Agendador do Windows
NOME_TAREFA = "FacebookAdsPipeline"

BASE_DIR  = Path(__file__).parent
LOG_FILE  = BASE_DIR / "agendamento.log"
PYTHON    = sys.executable
RUNNER    = BASE_DIR / "run_all.py"

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# EXECUTOR
# ─────────────────────────────────────────────

def executar_pipeline():
    log.info("Iniciando pipeline...")
    inicio = datetime.now()
    try:
        result = subprocess.run(
            [PYTHON, str(RUNNER)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        duracao = (datetime.now() - inicio).seconds
        if result.returncode == 0:
            log.info(f"Pipeline concluido com sucesso em {duracao}s.")
        else:
            log.error(f"Pipeline falhou (codigo {result.returncode}) em {duracao}s.")
            if result.stderr:
                for linha in result.stderr.strip().splitlines()[-5:]:
                    log.error(f"  {linha}")
    except Exception as e:
        log.exception(f"Erro inesperado ao executar pipeline: {e}")


# ─────────────────────────────────────────────
# MODO LOOP CONTINUO (schedule puro)
# ─────────────────────────────────────────────

def modo_loop():
    """Mantém o processo vivo e roda o pipeline no horário configurado."""
    try:
        import schedule
    except ImportError:
        log.error("Instale a biblioteca: pip install schedule")
        sys.exit(1)

    log.info(f"Agendamento iniciado — execucao diaria as {HORARIO_DIARIO}.")
    log.info("Pressione Ctrl+C para encerrar.")

    # Executa imediatamente na primeira vez
    executar_pipeline()

    schedule.every().day.at(HORARIO_DIARIO).do(executar_pipeline)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        log.info("Agendamento encerrado pelo usuario.")


# ─────────────────────────────────────────────
# AGENDADOR DE TAREFAS DO WINDOWS (schtasks)
# ─────────────────────────────────────────────

def instalar_tarefa():
    """Registra o pipeline no Agendador de Tarefas do Windows."""
    hora, minuto = HORARIO_DIARIO.split(":")
    cmd = [
        "schtasks", "/create",
        "/tn",  NOME_TAREFA,
        "/tr",  f'"{PYTHON}" "{RUNNER}"',
        "/sc",  "DAILY",
        "/st",  HORARIO_DIARIO,
        "/ru",  os.environ.get("USERNAME", "SYSTEM"),
        "/f",                    # sobrescreve se já existir
        "/rl", "HIGHEST",        # executa com privilégios elevados
    ]
    log.info(f"Registrando tarefa '{NOME_TAREFA}' para rodar diariamente as {HORARIO_DIARIO}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log.info("Tarefa registrada com sucesso no Agendador do Windows.")
        log.info(f"Para verificar: Agendador de Tarefas > Biblioteca > {NOME_TAREFA}")
    else:
        log.error(f"Falha ao registrar tarefa: {result.stderr.strip()}")
        log.error("Tente executar como Administrador.")


def remover_tarefa():
    """Remove a tarefa do Agendador de Tarefas do Windows."""
    cmd = ["schtasks", "/delete", "/tn", NOME_TAREFA, "/f"]
    log.info(f"Removendo tarefa '{NOME_TAREFA}'...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log.info("Tarefa removida com sucesso.")
    else:
        log.error(f"Falha ao remover: {result.stderr.strip()}")


def status_tarefa():
    """Exibe status da tarefa e últimas linhas do log."""
    # Status no Agendador do Windows
    print("\n--- Agendador de Tarefas do Windows ---")
    result = subprocess.run(
        ["schtasks", "/query", "/tn", NOME_TAREFA, "/fo", "LIST"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Tarefa '{NOME_TAREFA}' nao encontrada no Agendador.")

    # Últimas linhas do log
    print("--- Ultimas execucoes (agendamento.log) ---")
    if LOG_FILE.exists():
        linhas = LOG_FILE.read_text(encoding="utf-8").splitlines()
        for linha in linhas[-20:]:
            print(linha)
    else:
        print("Nenhum log encontrado ainda.")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Agendamento automatico do pipeline Facebook Ads"
    )
    parser.add_argument("--instalar", action="store_true",
                        help="Registra no Agendador de Tarefas do Windows")
    parser.add_argument("--remover",  action="store_true",
                        help="Remove do Agendador de Tarefas do Windows")
    parser.add_argument("--status",   action="store_true",
                        help="Exibe status e log recente")
    args = parser.parse_args()

    if args.instalar:
        instalar_tarefa()
    elif args.remover:
        remover_tarefa()
    elif args.status:
        status_tarefa()
    else:
        modo_loop()


if __name__ == "__main__":
    main()
