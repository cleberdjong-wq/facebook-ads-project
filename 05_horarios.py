"""
05_horarios.py
Extrai performance (cliques, impressões, gasto) por hora do dia.

Gera: horarios.csv
Colunas: hora, cliques, impressoes, gasto

Nota: a breakdown hourly_stats_aggregated_by_advertiser_time_zone retorna
      intervalos no formato "HH:00:00 - HH:59:00" — o script extrai só a hora.
"""

import csv
import re
from pathlib import Path
from config import account

OUTPUT = Path(__file__).parent / "horarios.csv"
DATE_PRESET = "last_30d"


def extrair_hora(intervalo: str) -> int:
    """
    Converte "09:00:00 - 09:59:00" → 9
    Converte "18:00:00 - 18:59:00" → 18
    """
    match = re.match(r"(\d{1,2}):\d{2}:\d{2}", intervalo.strip())
    if match:
        return int(match.group(1))
    return -1


def main():
    fields = [
        "clicks",
        "impressions",
        "spend",
    ]

    params = {
        "level": "account",
        "date_preset": DATE_PRESET,
        "breakdowns": ["hourly_stats_aggregated_by_advertiser_time_zone"],
    }

    print(f"Consultando performance por horário ({DATE_PRESET})...")
    insights = account.get_insights(fields=fields, params=params)

    # Agrupa por hora (0-23), somando todos os dias
    por_hora = {h: {"cliques": 0, "impressoes": 0, "gasto": 0.0} for h in range(24)}

    for row in insights:
        intervalo = row.get("hourly_stats_aggregated_by_advertiser_time_zone", "")
        hora = extrair_hora(intervalo)
        if hora < 0:
            continue

        por_hora[hora]["cliques"]    += int(row.get("clicks", 0))
        por_hora[hora]["impressoes"] += int(row.get("impressions", 0))
        por_hora[hora]["gasto"]      += float(row.get("spend", 0))

    rows = [
        {
            "hora":       h,
            "cliques":    por_hora[h]["cliques"],
            "impressoes": por_hora[h]["impressoes"],
            "gasto":      round(por_hora[h]["gasto"], 2),
        }
        for h in range(24)
    ]

    # Verifica se há dados (se todos zeros, API não retornou nada)
    if sum(r["cliques"] for r in rows) == 0:
        print("[AVISO] Nenhum dado horário retornado pela API.")
        return

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["hora", "cliques", "impressoes", "gasto"])
        writer.writeheader()
        writer.writerows(rows)

    pico_hora  = max(rows, key=lambda r: r["cliques"])
    total_cliques = sum(r["cliques"] for r in rows)
    print(f"[OK] {OUTPUT.name} salvo — 24 horas | Total de cliques: {total_cliques:,}")
    print(f"     Pico de cliques: {pico_hora['cliques']:,} às {pico_hora['hora']:02d}h")

    # Mini heatmap no terminal
    max_c = max(r["cliques"] for r in rows) or 1
    print("\n     Mapa de calor por hora:")
    for r in rows:
        bar = "#" * int(r["cliques"] / max_c * 30)
        print(f"     {r['hora']:02d}h |{bar:<30}| {r['cliques']:>6,}")


if __name__ == "__main__":
    main()
