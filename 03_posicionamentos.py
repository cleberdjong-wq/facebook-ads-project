"""
03_posicionamentos.py
Extrai distribuição de gasto e impressões por posicionamento (publisher_platform).

Gera: posicionamentos.csv
Colunas: posicionamento, gasto, impressoes
"""

import csv
from pathlib import Path
from config import account

OUTPUT = Path(__file__).parent / "posicionamentos.csv"
DATE_PRESET = "last_30d"

# Mapa de nomes técnicos da API → nomes amigáveis para o dashboard
NOMES_POSICIONAMENTO = {
    "facebook":          "Feed Facebook",
    "instagram":         "Feed Instagram",
    "audience_network":  "Audience Network",
    "messenger":         "Messenger",
    "instagram_stories": "Stories",
    "facebook_stories":  "Stories Facebook",
    "reels":             "Reels",
    "facebook_reels":    "Reels Facebook",
}


def nome_amigavel(platform, position=""):
    """Combina publisher_platform e placement para criar rótulo legível."""
    chave = f"{platform}_{position}".strip("_").lower() if position else platform.lower()
    return NOMES_POSICIONAMENTO.get(chave,
           NOMES_POSICIONAMENTO.get(platform.lower(), platform.title()))


def main():
    fields = [
        "spend",
        "impressions",
    ]

    params = {
        "level": "ad",
        "date_preset": DATE_PRESET,
        "breakdowns": ["publisher_platform", "platform_position"],
    }

    print(f"Consultando distribuição por posicionamento ({DATE_PRESET})...")
    insights = account.get_insights(fields=fields, params=params)

    # Agrupa por plataforma+posição
    agregado = {}
    for row in insights:
        platform = row.get("publisher_platform", "outro")
        position = row.get("platform_position", "")
        chave    = nome_amigavel(platform, position)

        if chave not in agregado:
            agregado[chave] = {"gasto": 0.0, "impressoes": 0}

        agregado[chave]["gasto"]      += float(row.get("spend", 0))
        agregado[chave]["impressoes"] += int(row.get("impressions", 0))

    if not agregado:
        print("[AVISO] Nenhum dado de posicionamento retornado.")
        return

    rows = [
        {"posicionamento": k, "gasto": round(v["gasto"], 2), "impressoes": v["impressoes"]}
        for k, v in sorted(agregado.items(), key=lambda x: -x[1]["gasto"])
    ]

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["posicionamento", "gasto", "impressoes"])
        writer.writeheader()
        writer.writerows(rows)

    total = sum(r["gasto"] for r in rows)
    print(f"[OK] {OUTPUT.name} salvo — {len(rows)} posicionamentos | Total: R$ {total:,.2f}")
    for r in rows:
        pct = r["gasto"] / total * 100 if total else 0
        print(f"     {r['posicionamento']:25s} R$ {r['gasto']:>10,.2f}  ({pct:.1f}%)")


if __name__ == "__main__":
    main()
