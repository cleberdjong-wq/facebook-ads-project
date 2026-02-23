"""
06_funil.py
Monta o funil de conversão a partir de métricas da conta (últimos 30 dias).

Estágios:
  Impressões → Alcance → Cliques → Visualizações de página → Leads → Conversões

Gera: funil.csv
Colunas: estagio, quantidade
"""

import csv
from pathlib import Path
from config import account

OUTPUT = Path(__file__).parent / "funil.csv"
DATE_PRESET = "last_30d"

# Mapeamento ação Facebook → estágio do funil
ACOES_CONVERSAO = [
    "purchase",              # Compra
    "complete_registration", # Registro completo
    "submit_application",    # Envio de formulário
    "lead",                  # Lead
    "contact",               # Contato
]

ACOES_LEAD = [
    "lead",
    "contact",
    "submit_application",
    "complete_registration",
]


def get_action_sum(actions, tipos):
    """Soma todos os valores das ações cujo action_type esteja em `tipos`."""
    if not actions:
        return 0
    total = 0
    vistos = set()
    for a in actions:
        t = a.get("action_type", "")
        if t in tipos and t not in vistos:
            total += int(float(a.get("value", 0)))
            vistos.add(t)
    return total


def main():
    fields = [
        "impressions",
        "reach",
        "clicks",
        "actions",
        "website_ctr",
    ]

    params = {
        "level": "account",
        "date_preset": DATE_PRESET,
    }

    print(f"Consultando métricas do funil ({DATE_PRESET})...")
    insights = account.get_insights(fields=fields, params=params)

    # Conta-level retorna normalmente 1 linha (ou poucos registros)
    impressoes = 0
    alcance    = 0
    cliques    = 0
    views_pag  = 0
    leads      = 0
    conversoes = 0

    for row in insights:
        impressoes += int(row.get("impressions", 0))
        alcance    += int(row.get("reach", 0))
        cliques    += int(row.get("clicks", 0))
        actions     = row.get("actions", [])

        views_pag  += get_action_sum(actions, {"landing_page_view", "view_content"})
        leads      += get_action_sum(actions, set(ACOES_LEAD))
        conversoes += get_action_sum(actions, set(ACOES_CONVERSAO))

    if impressoes == 0:
        print("[AVISO] Nenhum dado de funil retornado pela API.")
        return

    # Garante que os valores do funil são decrescentes (sanity check)
    views_pag  = min(views_pag,  cliques)
    leads      = min(leads,      views_pag if views_pag > 0 else cliques)
    conversoes = min(conversoes, leads if leads > 0 else cliques)

    estagios = [
        ("Impressoes",              impressoes),
        ("Alcance",                 alcance),
        ("Cliques",                 cliques),
        ("Visualizacoes de pagina", views_pag),
        ("Leads",                   leads),
        ("Conversoes",              conversoes),
    ]

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["estagio", "quantidade"])
        writer.writeheader()
        for estagio, qtd in estagios:
            writer.writerow({"estagio": estagio, "quantidade": qtd})

    print(f"[OK] {OUTPUT.name} salvo — funil com {len(estagios)} estagios\n")
    max_q = estagios[0][1] or 1
    print(f"     {'Estagio':<28} {'Quantidade':>12}  {'Taxa':>8}")
    print(f"     {'-'*52}")
    for estagio, qtd in estagios:
        taxa = qtd / max_q * 100
        print(f"     {estagio:<28} {qtd:>12,}  {taxa:>7.2f}%")


if __name__ == "__main__":
    main()
