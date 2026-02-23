"""
01_campanhas.py
Extrai métricas consolidadas por campanha (últimos 30 dias).

Gera: campanhas.csv
Colunas: campanha, gasto, impressoes, cliques, ctr, cpv, conversoes
"""

import csv
from pathlib import Path
from config import account

OUTPUT = Path(__file__).parent / "campanhas.csv"
DATE_PRESET = "last_30d"


def get_action_value(actions, action_type):
    """Extrai o valor de um tipo de ação da lista retornada pela API."""
    if not actions:
        return 0.0
    for a in actions:
        if a.get("action_type") == action_type:
            return float(a.get("value", 0))
    return 0.0


def get_cpv(cost_per_action, actions):
    """
    Retorna CPV (custo por visualização de vídeo).
    Usa cost_per_action_type[video_view] se disponível,
    caso contrário calcula spend / video_views.
    """
    if cost_per_action:
        for a in cost_per_action:
            if a.get("action_type") == "video_view":
                return float(a.get("value", 0))
    return 0.0


def main():
    fields = [
        "campaign_name",
        "spend",
        "impressions",
        "clicks",
        "ctr",
        "actions",
        "cost_per_action_type",
    ]

    params = {
        "level": "campaign",
        "date_preset": DATE_PRESET,
    }

    print(f"Consultando insights por campanha ({DATE_PRESET})...")
    insights = account.get_insights(fields=fields, params=params)

    rows = []
    for row in insights:
        campanha    = row.get("campaign_name", "Desconhecida")
        gasto       = float(row.get("spend", 0))
        impressoes  = int(row.get("impressions", 0))
        cliques     = int(row.get("clicks", 0))
        ctr         = float(row.get("ctr", 0))
        actions     = row.get("actions", [])
        cost_per_ac = row.get("cost_per_action_type", [])

        cpv         = get_cpv(cost_per_ac, actions)
        conversoes  = int(get_action_value(actions, "purchase") or
                         get_action_value(actions, "lead") or
                         get_action_value(actions, "complete_registration"))

        rows.append({
            "campanha":   campanha,
            "gasto":      round(gasto, 2),
            "impressoes": impressoes,
            "cliques":    cliques,
            "ctr":        round(ctr, 4),
            "cpv":        round(cpv, 6),
            "conversoes": conversoes,
        })

    if not rows:
        print("[AVISO] Nenhum dado retornado pela API.")
        return

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    total_gasto = sum(r["gasto"] for r in rows)
    print(f"[OK] {OUTPUT.name} salvo — {len(rows)} campanhas | Gasto total: R$ {total_gasto:,.2f}")


if __name__ == "__main__":
    main()
