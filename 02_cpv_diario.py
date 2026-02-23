"""
02_cpv_diario.py
Extrai a evolução diária do CPV (custo por visualização) nos últimos 30 dias.

Gera: cpv_diario.csv
Colunas: data, cpv
"""

import csv
from pathlib import Path
from config import account

OUTPUT = Path(__file__).parent / "cpv_diario.csv"
DATE_PRESET = "last_30d"


def calcular_cpv(row):
    """
    CPV = spend / video_views (visualizações de 3 segundos).
    Tenta cost_per_action_type[video_view] primeiro; fallback manual.
    """
    # Tentativa 1: campo direto
    cost_per_ac = row.get("cost_per_action_type", [])
    if cost_per_ac:
        for a in cost_per_ac:
            if a.get("action_type") == "video_view":
                return float(a.get("value", 0))

    # Tentativa 2: calcular manualmente
    spend = float(row.get("spend", 0))
    actions = row.get("actions", [])
    video_views = 0.0
    for a in actions:
        if a.get("action_type") == "video_view":
            video_views = float(a.get("value", 0))
            break

    if video_views > 0:
        return spend / video_views
    return 0.0


def main():
    fields = [
        "date_start",
        "spend",
        "actions",
        "cost_per_action_type",
    ]

    params = {
        "level": "account",
        "date_preset": DATE_PRESET,
        "time_increment": 1,          # 1 = breakdown diário
    }

    print(f"Consultando CPV diário ({DATE_PRESET})...")
    insights = account.get_insights(fields=fields, params=params)

    rows = []
    for row in insights:
        data = row.get("date_start", "")
        cpv  = calcular_cpv(row)

        if cpv > 0:                   # ignora dias sem impressões de vídeo
            rows.append({"data": data, "cpv": round(cpv, 6)})

    if not rows:
        print("[AVISO] Nenhum dado de CPV encontrado (verifique se há anúncios de vídeo ativos).")
        return

    rows.sort(key=lambda r: r["data"])

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["data", "cpv"])
        writer.writeheader()
        writer.writerows(rows)

    cpv_medio = sum(r["cpv"] for r in rows) / len(rows)
    print(f"[OK] {OUTPUT.name} salvo — {len(rows)} dias | CPV médio: R$ {cpv_medio:.6f}")


if __name__ == "__main__":
    main()
