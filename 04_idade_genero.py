"""
04_idade_genero.py
Extrai gasto e impressões segmentados por faixa etária e gênero.

Gera: idade_genero.csv
Colunas: idade, genero, gasto
"""

import csv
from pathlib import Path
from config import account

OUTPUT = Path(__file__).parent / "idade_genero.csv"
DATE_PRESET = "last_30d"

# Ordem canônica das faixas etárias para o dashboard
ORDEM_IDADES = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]

# Mapa gênero da API → português
GENERO_MAP = {
    "male":    "Masculino",
    "female":  "Feminino",
    "unknown": "Desconhecido",
}


def main():
    fields = [
        "spend",
        "impressions",
        "clicks",
    ]

    params = {
        "level": "ad",
        "date_preset": DATE_PRESET,
        "breakdowns": ["age", "gender"],
    }

    print(f"Consultando dados por idade e gênero ({DATE_PRESET})...")
    insights = account.get_insights(fields=fields, params=params)

    # Agrupa por (idade, genero)
    agregado = {}
    for row in insights:
        idade  = row.get("age", "desconhecido")
        genero = GENERO_MAP.get(row.get("gender", "unknown"), row.get("gender", "Outro"))
        chave  = (idade, genero)

        if chave not in agregado:
            agregado[chave] = {"gasto": 0.0, "impressoes": 0, "cliques": 0}

        agregado[chave]["gasto"]      += float(row.get("spend", 0))
        agregado[chave]["impressoes"] += int(row.get("impressions", 0))
        agregado[chave]["cliques"]    += int(row.get("clicks", 0))

    if not agregado:
        print("[AVISO] Nenhum dado demográfico retornado.")
        return

    # Ordena por faixa etária canônica
    def sort_key(item):
        idade, genero = item[0]
        idx = ORDEM_IDADES.index(idade) if idade in ORDEM_IDADES else 99
        return (idx, genero)

    rows = [
        {
            "idade":      k[0],
            "genero":     k[1],
            "gasto":      round(v["gasto"], 2),
            "impressoes": v["impressoes"],
            "cliques":    v["cliques"],
        }
        for k, v in sorted(agregado.items(), key=sort_key)
    ]

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["idade", "genero", "gasto", "impressoes", "cliques"])
        writer.writeheader()
        writer.writerows(rows)

    total = sum(r["gasto"] for r in rows)
    print(f"[OK] {OUTPUT.name} salvo — {len(rows)} segmentos | Total: R$ {total:,.2f}")
    print(f"\n     {'Idade':<10} {'Genero':<12} {'Gasto':>12}  {'Impressoes':>12}")
    print(f"     {'-'*50}")
    for r in rows:
        print(f"     {r['idade']:<10} {r['genero']:<12} R$ {r['gasto']:>9,.2f}  {r['impressoes']:>12,}")


if __name__ == "__main__":
    main()
