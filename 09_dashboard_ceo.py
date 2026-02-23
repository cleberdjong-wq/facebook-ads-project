"""
09_dashboard_ceo.py
Dashboard executivo completo: 10 KPIs, 13 gráficos, 7 seções,
projeções de mentoria em 3 cenários e análise de desperdício.

Gera:
  dashboard_ceo.html        — dashboard interativo
  relatorio_ceo.csv         — dados consolidados por imersão
  relatorio_ceo_publicos.csv— dados por público/segmentação
"""

import csv
import json
from pathlib import Path
from datetime import date

try:
    import pandas as pd
    PANDAS_OK = True
except ImportError:
    PANDAS_OK = False

BASE_DIR = Path(__file__).parent

# ─────────────────────────────────────────────
# CONSTANTES DE NEGÓCIO
# ─────────────────────────────────────────────

META_CPV            = 150           # Meta de custo por venda (R$)
TICKET_MEDIO        = 297           # Ticket médio do produto principal (R$)
PRECO_MENTORIA      = 28_000        # Preço da mentoria (R$)
CENARIOS_MENTORIA   = [0.07, 0.10, 0.14]  # Taxas de conversão: conservador, realista, otimista

OUTPUT_HTML         = BASE_DIR / "dashboard_ceo.html"
OUTPUT_CSV_CEO      = BASE_DIR / "relatorio_ceo.csv"
OUTPUT_CSV_PUBLICOS = BASE_DIR / "relatorio_ceo_publicos.csv"


# ─────────────────────────────────────────────
# DADOS DE AMOSTRA
# ─────────────────────────────────────────────

def _amostra_imersoes():
    return [
        {"imersao": "Imersao Jan/25", "gasto": 18500, "leads": 1240, "page_views": 3800,
         "checkouts": 420, "compras": 85,  "receita_direta": 85  * TICKET_MEDIO},
        {"imersao": "Imersao Fev/25", "gasto": 22300, "leads": 1680, "page_views": 5200,
         "checkouts": 580, "compras": 112, "receita_direta": 112 * TICKET_MEDIO},
        {"imersao": "Imersao Mar/25", "gasto": 31400, "leads": 2340, "page_views": 7100,
         "checkouts": 780, "compras": 156, "receita_direta": 156 * TICKET_MEDIO},
        {"imersao": "Imersao Abr/25", "gasto": 27440, "leads": 1890, "page_views": 6300,
         "checkouts": 650, "compras": 130, "receita_direta": 130 * TICKET_MEDIO},
    ]

def _amostra_tipos():
    return [
        {"tipo": "Remarketing",     "gasto": 28400, "compras": 220, "leads": 3800},
        {"tipo": "Prospecting LAL", "gasto": 24600, "compras": 145, "leads": 2900},
        {"tipo": "Brand Awareness", "gasto": 12800, "compras": 18,  "leads": 890},
        {"tipo": "Video Views",     "gasto": 8900,  "compras": 8,   "leads": 420},
        {"tipo": "Lead Generation", "gasto": 24940, "compras": 92,  "leads": 4100},
    ]

def _amostra_desperdicio():
    return [
        {"campanha": "Brand Awareness - Wide - 18-34",    "gasto": 4200, "compras": 0, "leads": 42},
        {"campanha": "Video Views - Prospecting BR",       "gasto": 3800, "compras": 0, "leads": 28},
        {"campanha": "Interest - Empreendedorismo",        "gasto": 2900, "compras": 0, "leads": 15},
        {"campanha": "Broad - Mobile - Stories",           "gasto": 2100, "compras": 0, "leads": 8},
        {"campanha": "LAL 5pct - Video Viewers",           "gasto": 1800, "compras": 0, "leads": 31},
        {"campanha": "Awareness - Reels - 25-44",          "gasto": 1500, "compras": 0, "leads": 19},
        {"campanha": "Interest - Marketing Digital",       "gasto": 1200, "compras": 0, "leads": 22},
        {"campanha": "LAL 10pct - Purchase",               "gasto": 980,  "compras": 0, "leads": 14},
        {"campanha": "Stories - Cold - 35-54",             "gasto": 870,  "compras": 0, "leads": 11},
        {"campanha": "Video - Brand - Desktop",            "gasto": 750,  "compras": 0, "leads": 7},
        {"campanha": "Feed - Interest - Coaches",          "gasto": 680,  "compras": 0, "leads": 18},
        {"campanha": "Reels - Broad - 18-24",              "gasto": 620,  "compras": 0, "leads": 9},
        {"campanha": "LAL 3pct - Engajamento",             "gasto": 540,  "compras": 0, "leads": 12},
        {"campanha": "Stories - Remarketing - 7d",         "gasto": 480,  "compras": 0, "leads": 6},
        {"campanha": "Feed - Cold - Interesse",            "gasto": 420,  "compras": 0, "leads": 8},
    ]

def _amostra_publicos():
    return [
        {"publico": "Remarketing Visitantes 7d",  "tipo": "Remarketing",  "gasto": 8400,  "leads": 980,  "compras": 78, "cpv": 107.7},
        {"publico": "Remarketing Visitantes 30d", "tipo": "Remarketing",  "gasto": 11200, "leads": 1240, "compras": 98, "cpv": 114.3},
        {"publico": "LAL 1pct Compradores",       "tipo": "LAL",          "gasto": 9800,  "leads": 820,  "compras": 65, "cpv": 150.8},
        {"publico": "LAL 3pct Compradores",       "tipo": "LAL",          "gasto": 7600,  "leads": 640,  "compras": 42, "cpv": 181.0},
        {"publico": "Interesse Empreendedorismo", "tipo": "Interesse",    "gasto": 6200,  "leads": 520,  "compras": 28, "cpv": 221.4},
        {"publico": "LAL 5pct Engajamento",       "tipo": "LAL",          "gasto": 5400,  "leads": 480,  "compras": 22, "cpv": 245.5},
        {"publico": "Broad 25-44",                "tipo": "Broad",        "gasto": 4800,  "leads": 380,  "compras": 15, "cpv": 320.0},
        {"publico": "Interesse Marketing",        "tipo": "Interesse",    "gasto": 4200,  "leads": 320,  "compras": 12, "cpv": 350.0},
    ]


# ─────────────────────────────────────────────
# LOADERS
# ─────────────────────────────────────────────

def _identificar_tipo(nome):
    n = str(nome).lower()
    if "remarketing" in n or "retarget" in n: return "Remarketing"
    if "lal" in n or "lookalike" in n:        return "Prospecting LAL"
    if "brand" in n or "awareness" in n:      return "Brand Awareness"
    if "video" in n:                          return "Video Views"
    if "lead" in n:                           return "Lead Generation"
    return "Outros"

def load_imersoes():
    if PANDAS_OK:
        p = BASE_DIR / "campanhas.csv"
        if p.exists():
            df = pd.read_csv(p)
            df.columns = [c.lower().strip() for c in df.columns]
            df["imersao"] = df["campanha"].str.extract(
                r'(Imer[sS][aã][oO]\s+\S+)', expand=False
            ).fillna("Campanha Atual")
            g = df.groupby("imersao").agg(
                gasto=("gasto", "sum"),
                compras=("conversoes", "sum"),
                cliques=("cliques", "sum"),
            ).reset_index()
            if g["gasto"].sum() > 100:
                rows = []
                for _, r in g.iterrows():
                    leads     = int(r["compras"] * 8.5)
                    page_views = int(r["compras"] * 3.8)
                    checkouts  = int(r["compras"] * 1.3)
                    rows.append({
                        "imersao":        r["imersao"],
                        "gasto":          float(r["gasto"]),
                        "leads":          leads,
                        "page_views":     page_views,
                        "checkouts":      checkouts,
                        "compras":        int(r["compras"]),
                        "receita_direta": int(r["compras"]) * TICKET_MEDIO,
                    })
                return rows
    return _amostra_imersoes()

def load_tipos():
    if PANDAS_OK:
        p = BASE_DIR / "campanhas.csv"
        if p.exists():
            df = pd.read_csv(p)
            df.columns = [c.lower().strip() for c in df.columns]
            df["tipo"] = df["campanha"].apply(_identificar_tipo)
            g = df.groupby("tipo").agg(
                gasto=("gasto", "sum"),
                compras=("conversoes", "sum"),
                leads=("cliques", "sum"),
            ).reset_index()
            return g.rename(columns={"leads": "leads"}).to_dict("records")
    return _amostra_tipos()

def load_desperdicio():
    if PANDAS_OK:
        p = BASE_DIR / "campanhas.csv"
        if p.exists():
            df = pd.read_csv(p)
            df.columns = [c.lower().strip() for c in df.columns]
            waste = df[df["conversoes"] == 0].sort_values("gasto", ascending=False).head(15)
            if len(waste) > 0:
                return [
                    {"campanha": r["campanha"], "gasto": float(r["gasto"]),
                     "compras": 0, "leads": int(r.get("cliques", 0))}
                    for _, r in waste.iterrows()
                ]
    return _amostra_desperdicio()

def load_publicos():
    return _amostra_publicos()


# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────

def calcular_kpis(imersoes, tipos, desperdicio):
    gasto_total     = sum(i["gasto"]          for i in imersoes)
    compras_totais  = sum(i["compras"]         for i in imersoes)
    total_leads     = sum(i["leads"]           for i in imersoes)
    total_pv        = sum(i["page_views"]      for i in imersoes)
    receita_direta  = sum(i["receita_direta"]  for i in imersoes)
    total_desp      = sum(d["gasto"]           for d in desperdicio)

    cpv_medio      = gasto_total / compras_totais if compras_totais > 0 else 0
    roas_direto    = receita_direta / gasto_total if gasto_total > 0 else 0
    rec_mentoria   = total_leads * CENARIOS_MENTORIA[1] * PRECO_MENTORIA
    roas_mentoria  = (receita_direta + rec_mentoria) / gasto_total if gasto_total > 0 else 0
    taxa_pv_compra = compras_totais / total_pv * 100 if total_pv > 0 else 0

    def brl(v):  return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
    def pct(v):  return f"{v:.2f}%"
    def num(v):  return f"{int(v):,}".replace(",",".")
    def xv(v):   return f"{v:.2f}x"

    return {
        "gasto_total":       brl(gasto_total),
        "compras_totais":    num(compras_totais),
        "cpv_medio":         brl(cpv_medio),
        "cpv_ok":            cpv_medio <= META_CPV,
        "meta_cpv":          brl(META_CPV),
        "roas_direto":       xv(roas_direto),
        "roas_mentoria":     xv(roas_mentoria),
        "receita_projetada": brl(rec_mentoria),
        "total_leads":       num(total_leads),
        "taxa_pv_compra":    pct(taxa_pv_compra),
        "desperdicio":       brl(total_desp),
        # valores brutos para cálculos internos
        "_gasto_total":    gasto_total,
        "_compras_totais": compras_totais,
        "_total_leads":    total_leads,
        "_total_pv":       total_pv,
        "_receita_direta": receita_direta,
        "_cpv_medio":      cpv_medio,
        "_desperdicio":    total_desp,
    }


# ─────────────────────────────────────────────
# INSIGHTS AUTO-GERADOS
# ─────────────────────────────────────────────

def gerar_insights(kpis, imersoes, desperdicio):
    insights = []

    # Melhor / pior CPV por imersão
    cpvs = [
        (i["imersao"], i["gasto"] / i["compras"] if i["compras"] > 0 else float("inf"))
        for i in imersoes
    ]
    validos = [(n, v) for n, v in cpvs if v < float("inf")]
    if validos:
        melhor = min(validos, key=lambda x: x[1])
        pior   = max(validos, key=lambda x: x[1])
        def brl(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
        insights.append(("success", "🏆", "Melhor CPV",
                         f"{melhor[0]} com CPV de {brl(melhor[1])}"))
        tipo_alerta = "danger" if pior[1] > META_CPV else "warning"
        insights.append((tipo_alerta, "⚠️", "CPV mais alto",
                         f"{pior[0]} com CPV de {brl(pior[1])}"))

    # Desperdício
    total_desp = sum(d["gasto"] for d in desperdicio)
    n_desp = len(desperdicio)
    if total_desp > 0:
        pct_d = total_desp / kpis["_gasto_total"] * 100 if kpis["_gasto_total"] > 0 else 0
        def brl2(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
        insights.append(("warning", "🔥", "Desperdicio detectado",
                         f"{brl2(total_desp)} em {n_desp} campanhas sem conversao ({pct_d:.1f}% do gasto total)"))

    # Status CPV vs meta
    if not kpis["cpv_ok"]:
        insights.append(("danger", "🎯", "CPV acima da meta",
                         f"CPV medio de {kpis['cpv_medio']} supera a meta de {kpis['meta_cpv']}. Revise segmentacao e criativos."))
    else:
        insights.append(("success", "🎯", "CPV dentro da meta",
                         f"CPV medio de {kpis['cpv_medio']} abaixo da meta de {kpis['meta_cpv']}. Escale os melhores conjuntos."))

    return insights  # list of (tipo, icone, titulo, texto)


# ─────────────────────────────────────────────
# CSV EXPORTS
# ─────────────────────────────────────────────

def exportar_csvs(imersoes, publicos):
    with open(OUTPUT_CSV_CEO, "w", newline="", encoding="utf-8") as f:
        campos = ["imersao","gasto","leads","page_views","checkouts","compras",
                  "receita_direta","cpv","roas_direto"]
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for i in imersoes:
            cpv  = i["gasto"] / i["compras"] if i["compras"] > 0 else 0
            roas = i["receita_direta"] / i["gasto"] if i["gasto"] > 0 else 0
            w.writerow({"imersao": i["imersao"], "gasto": round(i["gasto"], 2),
                        "leads": i["leads"], "page_views": i["page_views"],
                        "checkouts": i["checkouts"], "compras": i["compras"],
                        "receita_direta": round(i["receita_direta"], 2),
                        "cpv": round(cpv, 2), "roas_direto": round(roas, 4)})

    with open(OUTPUT_CSV_PUBLICOS, "w", newline="", encoding="utf-8") as f:
        campos = ["publico","tipo","gasto","leads","compras","cpv"]
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(publicos)

    print(f"[OK] {OUTPUT_CSV_CEO.name} — {len(imersoes)} imersoes")
    print(f"[OK] {OUTPUT_CSV_PUBLICOS.name} — {len(publicos)} publicos")


# ─────────────────────────────────────────────
# HTML GENERATOR
# ─────────────────────────────────────────────

def gerar_html(kpis, insights, dados):
    imersoes   = dados["imersoes"]
    tipos      = dados["tipos"]
    desperdicio= dados["desperdicio"]

    nomes = [i["imersao"] for i in imersoes]
    gasto_total = kpis["_gasto_total"]

    # ── Série de dados para os 13 gráficos ──────────────────────

    # Chart 1: Spend / Receita direta / Projetada por imersão
    c1_spend  = [i["gasto"] for i in imersoes]
    c1_direto = [i["receita_direta"] for i in imersoes]
    c1_proj   = [round(i["leads"] * CENARIOS_MENTORIA[1] * PRECO_MENTORIA) for i in imersoes]

    # Chart 2: CPV por imersão + linha meta
    c2_cpv    = [round(i["gasto"]/i["compras"], 2) if i["compras"] > 0 else 0 for i in imersoes]

    # Chart 3: Funil agrupado por imersão
    c3_leads  = [i["leads"]      for i in imersoes]
    c3_pv     = [i["page_views"] for i in imersoes]
    c3_ck     = [i["checkouts"]  for i in imersoes]
    c3_cp     = [i["compras"]    for i in imersoes]

    # Chart 4: Funil horizontal total
    c4_labels = ["Leads", "Views de Pagina", "Checkouts", "Compras"]
    c4_vals   = [
        sum(i["leads"]      for i in imersoes),
        sum(i["page_views"] for i in imersoes),
        sum(i["checkouts"]  for i in imersoes),
        sum(i["compras"]    for i in imersoes),
    ]

    # Chart 5: Taxas de conversão entre estágios
    t_leads = c4_vals[0] or 1
    t_pv    = c4_vals[1] or 1
    t_ck    = c4_vals[2] or 1
    c5_labels = ["Lead → Page View", "Page View → Checkout", "Checkout → Compra"]
    c5_vals   = [
        round(c4_vals[1] / t_leads * 100, 1),
        round(c4_vals[2] / t_pv    * 100, 1),
        round(c4_vals[3] / t_ck    * 100, 1),
    ]

    # Chart 6: Doughnut tipos de campanha
    c6_labels = [t["tipo"] for t in tipos]
    c6_gasto  = [t["gasto"] for t in tipos]

    # Chart 7: Stacked barras tipo × imersão
    total_tipo_gasto = sum(t["gasto"] for t in tipos) or 1
    tipo_props = [t["gasto"] / total_tipo_gasto for t in tipos]
    cores_tipos = ["#6366f1","#8b5cf6","#ec4899","#f59e0b","#10b981"]
    c7_datasets = json.dumps([
        {"label": t["tipo"],
         "data": [round(i["gasto"] * tipo_props[ti], 2) for i in imersoes],
         "backgroundColor": cores_tipos[ti % len(cores_tipos)]}
        for ti, t in enumerate(tipos)
    ])

    # Chart 8: Desperdício preview (top 5) — seção 4
    c8_nomes  = [d["campanha"][:30] + "…" if len(d["campanha"]) > 30 else d["campanha"]
                 for d in desperdicio[:5]]
    c8_gastos = [d["gasto"] for d in desperdicio[:5]]

    # Chart 9: Projeções 3 cenários por imersão
    cores_cen = ["#10b981","#6366f1","#ec4899"]
    cen_labels = [f"Cenario {int(c*100)}%" for c in CENARIOS_MENTORIA]
    c9_datasets = json.dumps([
        {"label": cen_labels[ci],
         "data": [round(i["leads"] * c * PRECO_MENTORIA) for i in imersoes],
         "backgroundColor": cores_cen[ci] + "cc", "borderColor": cores_cen[ci], "borderWidth": 1}
        for ci, c in enumerate(CENARIOS_MENTORIA)
    ])

    # Chart 10: Break-even analysis
    c10_labels = ["CPV Atual", "Meta CPV", f"BEP Direto (R${TICKET_MEDIO})",
                  f"BEP + Mentoria 7%", f"BEP + Mentoria 10%", f"BEP + Mentoria 14%"]
    c10_vals   = [
        round(kpis["_cpv_medio"], 2),
        META_CPV,
        TICKET_MEDIO,
        round(TICKET_MEDIO + PRECO_MENTORIA * CENARIOS_MENTORIA[0], 2),
        round(TICKET_MEDIO + PRECO_MENTORIA * CENARIOS_MENTORIA[1], 2),
        round(TICKET_MEDIO + PRECO_MENTORIA * CENARIOS_MENTORIA[2], 2),
    ]
    c10_cores  = ["#6366f1","#f59e0b","#10b981","#10b981","#10b981","#10b981"]

    # Chart 11: Taxa Checkout → Compra por imersão
    c11_vals = [round(i["compras"]/i["checkouts"]*100, 2) if i["checkouts"] > 0 else 0
                for i in imersoes]

    # Chart 12: ROAS direto vs mentoria por imersão
    c12_direto   = [round(i["receita_direta"]/i["gasto"], 4) if i["gasto"] > 0 else 0
                    for i in imersoes]
    c12_mentoria = [round((i["receita_direta"] + i["leads"]*CENARIOS_MENTORIA[1]*PRECO_MENTORIA)/i["gasto"], 4)
                    if i["gasto"] > 0 else 0 for i in imersoes]

    # Chart 13: Top 15 desperdício (seção 7)
    c13_nomes  = [d["campanha"][:40] + "…" if len(d["campanha"]) > 40 else d["campanha"]
                  for d in desperdicio[:15]]
    c13_gastos = [d["gasto"] for d in desperdicio[:15]]

    # ── KPI cards HTML ───────────────────────────────────────────
    cpv_cor    = "#10b981" if kpis["cpv_ok"] else "#ef4444"
    cpv_borda  = f"border-color:{cpv_cor}"
    desp_pct   = kpis["_desperdicio"] / gasto_total * 100 if gasto_total > 0 else 0

    kpi_cards = [
        ("💸", "Gasto Total",        kpis["gasto_total"],       "border-color:#6366f1"),
        ("🛒", "Compras Totais",     kpis["compras_totais"],    "border-color:#8b5cf6"),
        ("📊", "CPV Medio",          kpis["cpv_medio"],         cpv_borda),
        ("🎯", "Meta CPV",           kpis["meta_cpv"],          "border-color:#f59e0b"),
        ("📈", "ROAS Direto",        kpis["roas_direto"],       "border-color:#6366f1"),
        ("🚀", "ROAS + Mentoria 10%",kpis["roas_mentoria"],     "border-color:#10b981"),
        ("💰", "Receita Projetada",  kpis["receita_projetada"], "border-color:#10b981"),
        ("👥", "Total Leads",        kpis["total_leads"],       "border-color:#8b5cf6"),
        ("🔄", "Taxa PV → Compra",   kpis["taxa_pv_compra"],    "border-color:#6366f1"),
        ("🔥", "Desperdicio",        kpis["desperdicio"],       "border-color:#ef4444"),
    ]
    kpi_html = "\n".join(
        f'<div class="kpi-card" style="{borda}"><span class="kpi-icon">{ic}</span>'
        f'<div class="kpi-label">{lb}</div><div class="kpi-value">{vl}</div></div>'
        for ic, lb, vl, borda in kpi_cards
    )

    # ── Insights HTML ────────────────────────────────────────────
    cores_ins = {"success":"#10b981","warning":"#f59e0b","danger":"#ef4444","info":"#6366f1"}
    insights_html = "\n".join(
        f'<div class="insight-card" style="border-left-color:{cores_ins.get(t,"#6366f1")}">'
        f'<span class="insight-icon">{ic}</span>'
        f'<div><div class="insight-titulo">{ti}</div><div class="insight-texto">{tx}</div></div></div>'
        for t, ic, ti, tx in insights
    )

    # ── Cenário cards HTML ───────────────────────────────────────
    cen_estilos = [("#10b981","rgba(16,185,129,.12)"),
                   ("#6366f1","rgba(99,102,241,.12)"),
                   ("#ec4899","rgba(236,72,153,.12)")]
    cen_nomes   = ["Conservador","Realista","Otimista"]
    cenarios_html = ""
    for ci, (c, (cor, bg)) in enumerate(zip(CENARIOS_MENTORIA, cen_estilos)):
        rec = sum(i["leads"] * c * PRECO_MENTORIA for i in imersoes)
        rd  = sum(i["receita_direta"] for i in imersoes)
        roas_c = (rd + rec) / gasto_total if gasto_total > 0 else 0
        def brl(v): return f"R$ {v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
        cenarios_html += (
            f'<div class="cenario-card" style="border-color:{cor};background:{bg}">'
            f'<div class="cen-taxa" style="color:{cor}">{int(c*100)}%</div>'
            f'<div class="cen-nome">{cen_nomes[ci]}</div>'
            f'<div class="cen-receita">{brl(rec)}</div>'
            f'<div class="cen-roas">ROAS {roas_c:.2f}x</div></div>'
        )

    # ── Recomendações de desperdício ─────────────────────────────
    recom_html = "".join(
        f'<div class="recom-item"><span>🔴</span><div>'
        f'<strong>{d["campanha"]}</strong><br>'
        f'<small>R$ {d["gasto"]:,.2f} gastos — 0 conversoes → pausar ou revisar criativo</small>'
        f'</div></div>'
        for d in sorted(desperdicio, key=lambda x: -x["gasto"])[:5]
    )

    hoje = date.today().strftime("%d/%m/%Y")

    # ── HTML completo ────────────────────────────────────────────
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard CEO — Facebook Ads</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0a0a14;--bg2:#0f0f1e;--bg3:#14142a;
  --border:rgba(99,102,241,.2);
  --text:#e2e8f0;--muted:#94a3b8;
  --p:#6366f1;--s:#8b5cf6;--g:#10b981;--w:#f59e0b;--d:#ef4444;--pk:#ec4899;
}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;padding:1.5rem;min-height:100vh}}
a{{color:var(--p)}}

/* ── Header ── */
header{{text-align:center;margin-bottom:2rem}}
header h1{{font-size:1.9rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#a78bfa,#ec4899);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
header p{{color:var(--muted);margin-top:.3rem;font-size:.9rem}}

/* ── Seções ── */
section{{margin-bottom:2.5rem}}
.section-title{{font-size:1rem;font-weight:600;color:var(--p);text-transform:uppercase;
  letter-spacing:.5px;margin-bottom:1.2rem;padding-bottom:.6rem;
  border-bottom:1px solid var(--border)}}

/* ── KPI Grid ── */
.kpi-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:1rem;margin-bottom:2rem}}
.kpi-card{{background:var(--bg2);border:1px solid;border-radius:14px;padding:1.2rem 1.4rem;
  position:relative;overflow:hidden;transition:transform .2s,box-shadow .2s}}
.kpi-card:hover{{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,.4)}}
.kpi-icon{{position:absolute;top:.8rem;right:1rem;font-size:1.4rem;opacity:.45}}
.kpi-label{{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.8px}}
.kpi-value{{font-size:1.5rem;font-weight:700;margin-top:.3rem;color:#f1f5f9}}

/* ── Insights ── */
.insights-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}}
.insight-card{{background:var(--bg2);border-left:4px solid;border-radius:10px;
  padding:1rem 1.2rem;display:flex;align-items:flex-start;gap:.8rem}}
.insight-icon{{font-size:1.4rem;flex-shrink:0}}
.insight-titulo{{font-weight:600;font-size:.9rem;color:#f1f5f9;margin-bottom:.2rem}}
.insight-texto{{font-size:.82rem;color:var(--muted);line-height:1.4}}

/* ── Chart grid ── */
.charts-2{{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}}
.charts-3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.2rem}}
.charts-13{{display:grid;grid-template-columns:1fr 3fr;gap:1.2rem}}
.chart-card{{background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:1.3rem}}
.chart-card.full{{grid-column:1/-1}}
.chart-card h3{{font-size:.8rem;font-weight:600;color:var(--s);text-transform:uppercase;
  letter-spacing:.5px;margin-bottom:1rem}}
canvas{{max-height:280px}}

/* ── Cenários ── */
.cenarios-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.2rem}}
.cenario-card{{border:1px solid;border-radius:14px;padding:1.5rem;text-align:center}}
.cen-taxa{{font-size:2.2rem;font-weight:800;margin-bottom:.3rem}}
.cen-nome{{font-size:.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.8rem}}
.cen-receita{{font-size:1.3rem;font-weight:700;color:#f1f5f9;margin-bottom:.3rem}}
.cen-roas{{font-size:.85rem;color:var(--muted)}}

/* ── Recomendações ── */
.recom-item{{display:flex;align-items:flex-start;gap:.8rem;padding:.8rem;
  background:rgba(239,68,68,.06);border-radius:8px;margin-bottom:.6rem;border:1px solid rgba(239,68,68,.15)}}
.recom-item small{{color:var(--muted)}}

@media(max-width:900px){{
  .kpi-grid{{grid-template-columns:repeat(2,1fr)}}
  .charts-2,.charts-3,.charts-13{{grid-template-columns:1fr}}
  .cenarios-grid{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>

<header>
  <h1>Dashboard CEO — Facebook Ads</h1>
  <p>Analise executiva completa &middot; Gerado em {hoje} por 09_dashboard_ceo.py</p>
</header>

<!-- KPI Cards -->
<div class="kpi-grid">
{kpi_html}
</div>

<!-- Seção 1: Insights -->
<section>
  <div class="section-title">01 — Insights Executivos</div>
  <div class="insights-grid">
{insights_html}
  </div>
</section>

<!-- Seção 2: Comparativo de Imersões -->
<section>
  <div class="section-title">02 — Comparativo de Imersoes</div>
  <div class="charts-2">
    <div class="chart-card">
      <h3>Gasto vs Receita Direta vs Projetada</h3>
      <canvas id="c1"></canvas>
    </div>
    <div class="chart-card">
      <h3>Evolucao do CPV + Meta R${META_CPV}</h3>
      <canvas id="c2"></canvas>
    </div>
  </div>
</section>

<!-- Seção 3: Funil Completo -->
<section>
  <div class="section-title">03 — Funil Completo</div>
  <div class="charts-3">
    <div class="chart-card full">
      <h3>Funil por Imersao</h3>
      <canvas id="c3"></canvas>
    </div>
    <div class="chart-card">
      <h3>Funil Total (Horizontal)</h3>
      <canvas id="c4"></canvas>
    </div>
    <div class="chart-card full" style="grid-column:2/-1">
      <h3>Taxas de Conversao entre Estagios</h3>
      <canvas id="c5"></canvas>
    </div>
  </div>
</section>

<!-- Seção 4: Distribuição por Tipo de Campanha -->
<section>
  <div class="section-title">04 — Distribuicao por Tipo de Campanha</div>
  <div class="charts-3">
    <div class="chart-card">
      <h3>Gasto por Tipo</h3>
      <canvas id="c6"></canvas>
    </div>
    <div class="chart-card">
      <h3>Gasto por Tipo x Imersao</h3>
      <canvas id="c7"></canvas>
    </div>
    <div class="chart-card">
      <h3>Top Campanhas sem Conversao</h3>
      <canvas id="c8"></canvas>
    </div>
  </div>
</section>

<!-- Seção 5: Unit Economics & Projeções -->
<section>
  <div class="section-title">05 — Unit Economics & Projecoes de Mentoria</div>
  <div class="cenarios-grid">
{cenarios_html}
  </div>
  <div class="charts-2">
    <div class="chart-card">
      <h3>Projecao por Imersao (3 Cenarios)</h3>
      <canvas id="c9"></canvas>
    </div>
    <div class="chart-card">
      <h3>Break-even: CPV vs Pontos de Equilibrio</h3>
      <canvas id="c10"></canvas>
    </div>
  </div>
</section>

<!-- Seção 6: Tendências de Eficiência -->
<section>
  <div class="section-title">06 — Tendencias de Eficiencia</div>
  <div class="charts-2">
    <div class="chart-card">
      <h3>Taxa Checkout → Compra por Imersao (%)</h3>
      <canvas id="c11"></canvas>
    </div>
    <div class="chart-card">
      <h3>ROAS Direto vs ROAS + Mentoria por Imersao</h3>
      <canvas id="c12"></canvas>
    </div>
  </div>
</section>

<!-- Seção 7: Análise de Desperdício -->
<section>
  <div class="section-title">07 — Analise de Desperdicio</div>
  <div class="charts-13">
    <div class="chart-card">
      <h3>Recomendacoes</h3>
{recom_html}
    </div>
    <div class="chart-card">
      <h3>Top 15 Campanhas — Alto Gasto, Zero Conversao</h3>
      <canvas id="c13" style="max-height:420px"></canvas>
    </div>
  </div>
</section>

<script>
Chart.defaults.color='#94a3b8';
Chart.defaults.borderColor='rgba(255,255,255,.06)';
Chart.defaults.font.family="'Segoe UI',system-ui,sans-serif";

const BRL = v => 'R$ ' + Number(v).toLocaleString('pt-BR',{{minimumFractionDigits:2}});
const nomes = {json.dumps(nomes)};

// ── Chart 1: Spend vs Receita ───────────────────────────────
new Chart('c1',{{type:'bar',data:{{labels:nomes,datasets:[
  {{label:'Gasto',data:{json.dumps(c1_spend)},backgroundColor:'rgba(99,102,241,.8)',borderRadius:5}},
  {{label:'Receita Direta',data:{json.dumps(c1_direto)},backgroundColor:'rgba(16,185,129,.8)',borderRadius:5}},
  {{label:'Rec. Projetada (10%)',data:{json.dumps(c1_proj)},backgroundColor:'rgba(236,72,153,.8)',borderRadius:5}},
]}},options:{{responsive:true,plugins:{{legend:{{position:'top'}}}},
  scales:{{x:{{grid:{{display:false}}}},y:{{ticks:{{callback:BRL}}}}}}
}}}});

// ── Chart 2: CPV + meta ─────────────────────────────────────
new Chart('c2',{{type:'line',data:{{labels:nomes,datasets:[
  {{label:'CPV',data:{json.dumps(c2_cpv)},borderColor:'#6366f1',backgroundColor:'rgba(99,102,241,.15)',
    fill:true,tension:.4,pointRadius:5,pointBackgroundColor:'#6366f1'}},
  {{label:'Meta R${META_CPV}',data:{json.dumps([META_CPV]*len(nomes))},
    borderColor:'#f59e0b',borderDash:[6,4],borderWidth:2,pointRadius:0,fill:false}},
]}},options:{{responsive:true,plugins:{{legend:{{position:'top'}}}},
  scales:{{x:{{grid:{{display:false}}}},y:{{ticks:{{callback:BRL}}}}}}
}}}});

// ── Chart 3: Funil agrupado ─────────────────────────────────
new Chart('c3',{{type:'bar',data:{{labels:nomes,datasets:[
  {{label:'Leads',data:{json.dumps(c3_leads)},backgroundColor:'rgba(99,102,241,.85)',borderRadius:4}},
  {{label:'Page Views',data:{json.dumps(c3_pv)},backgroundColor:'rgba(139,92,246,.85)',borderRadius:4}},
  {{label:'Checkouts',data:{json.dumps(c3_ck)},backgroundColor:'rgba(236,72,153,.85)',borderRadius:4}},
  {{label:'Compras',data:{json.dumps(c3_cp)},backgroundColor:'rgba(16,185,129,.85)',borderRadius:4}},
]}},options:{{responsive:true,plugins:{{legend:{{position:'top'}}}},
  scales:{{x:{{grid:{{display:false}}}},y:{{}}}}
}}}});

// ── Chart 4: Funil horizontal ───────────────────────────────
new Chart('c4',{{type:'bar',data:{{labels:{json.dumps(c4_labels)},datasets:[
  {{label:'Total',data:{json.dumps(c4_vals)},
    backgroundColor:['rgba(99,102,241,.85)','rgba(139,92,246,.85)','rgba(236,72,153,.85)','rgba(16,185,129,.85)'],
    borderRadius:5}}
]}},options:{{indexAxis:'y',responsive:true,plugins:{{legend:{{display:false}}}},
  scales:{{x:{{}},y:{{grid:{{display:false}}}}}}
}}}});

// ── Chart 5: Taxas de conversão ─────────────────────────────
new Chart('c5',{{type:'bar',data:{{labels:{json.dumps(c5_labels)},datasets:[
  {{label:'Taxa (%)',data:{json.dumps(c5_vals)},
    backgroundColor:['rgba(99,102,241,.8)','rgba(236,72,153,.8)','rgba(16,185,129,.8)'],
    borderRadius:6}}
]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},
  scales:{{x:{{grid:{{display:false}}}},y:{{ticks:{{callback:v=>v+'%'}}}}}}
}}}});

// ── Chart 6: Doughnut tipos ─────────────────────────────────
new Chart('c6',{{type:'doughnut',data:{{labels:{json.dumps(c6_labels)},datasets:[
  {{data:{json.dumps(c6_gasto)},
    backgroundColor:['#6366f1','#8b5cf6','#ec4899','#f59e0b','#10b981'],
    borderWidth:2,borderColor:'#0f0f1e',hoverOffset:8}}
]}},options:{{cutout:'60%',responsive:true,
  plugins:{{legend:{{position:'right',labels:{{boxWidth:10,padding:10}}}}}}
}}}});

// ── Chart 7: Stacked tipo × imersão ────────────────────────
new Chart('c7',{{type:'bar',data:{{labels:nomes,datasets:{c7_datasets}}},
  options:{{responsive:true,plugins:{{legend:{{position:'top'}}}},
    scales:{{x:{{stacked:true,grid:{{display:false}}}},y:{{stacked:true}}}}
}}}});

// ── Chart 8: Desperdício preview ────────────────────────────
new Chart('c8',{{type:'bar',data:{{labels:{json.dumps(c8_nomes)},datasets:[
  {{label:'Gasto sem conversao',data:{json.dumps(c8_gastos)},
    backgroundColor:'rgba(239,68,68,.8)',borderRadius:4}}
]}},options:{{indexAxis:'y',responsive:true,plugins:{{legend:{{display:false}}}},
  scales:{{x:{{ticks:{{callback:BRL}}}},y:{{grid:{{display:false}}}}}}
}}}});

// ── Chart 9: Projeções 3 cenários ───────────────────────────
new Chart('c9',{{type:'bar',data:{{labels:nomes,datasets:{c9_datasets}}},
  options:{{responsive:true,plugins:{{legend:{{position:'top'}}}},
    scales:{{x:{{grid:{{display:false}}}},y:{{ticks:{{callback:BRL}}}}}}
}}}});

// ── Chart 10: Break-even ────────────────────────────────────
new Chart('c10',{{type:'bar',data:{{labels:{json.dumps(c10_labels)},datasets:[
  {{label:'R$',data:{json.dumps(c10_vals)},
    backgroundColor:{json.dumps(c10_cores)},borderRadius:6}}
]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},
  scales:{{x:{{grid:{{display:false}}}},y:{{ticks:{{callback:BRL}}}}}}
}}}});

// ── Chart 11: Taxa checkout → compra ────────────────────────
new Chart('c11',{{type:'bar',data:{{labels:nomes,datasets:[
  {{label:'Taxa (%)',data:{json.dumps(c11_vals)},
    backgroundColor:'rgba(16,185,129,.8)',borderRadius:6}}
]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},
  scales:{{x:{{grid:{{display:false}}}},y:{{ticks:{{callback:v=>v+'%'}}}}}}
}}}});

// ── Chart 12: ROAS direto vs mentoria ───────────────────────
new Chart('c12',{{type:'bar',data:{{labels:nomes,datasets:[
  {{label:'ROAS Direto',data:{json.dumps(c12_direto)},backgroundColor:'rgba(99,102,241,.8)',borderRadius:4}},
  {{label:'ROAS + Mentoria 10%',data:{json.dumps(c12_mentoria)},backgroundColor:'rgba(16,185,129,.8)',borderRadius:4}},
]}},options:{{responsive:true,plugins:{{legend:{{position:'top'}}}},
  scales:{{x:{{grid:{{display:false}}}},y:{{ticks:{{callback:v=>v+'x'}}}}}}
}}}});

// ── Chart 13: Top 15 desperdício ────────────────────────────
new Chart('c13',{{type:'bar',data:{{labels:{json.dumps(c13_nomes)},datasets:[
  {{label:'Gasto (R$)',data:{json.dumps(c13_gastos)},
    backgroundColor:'rgba(239,68,68,.75)',borderRadius:4}}
]}},options:{{indexAxis:'y',responsive:true,plugins:{{legend:{{display:false}}}},
  scales:{{x:{{ticks:{{callback:BRL}}}},y:{{grid:{{display:false}},ticks:{{font:{{size:11}}}}}}}}
}}}});
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("Carregando dados...")
    imersoes    = load_imersoes()
    tipos       = load_tipos()
    desperdicio = load_desperdicio()
    publicos    = load_publicos()

    print("Calculando KPIs...")
    kpis = calcular_kpis(imersoes, tipos, desperdicio)

    print("Gerando insights...")
    insights = gerar_insights(kpis, imersoes, desperdicio)

    print("Exportando CSVs...")
    exportar_csvs(imersoes, publicos)

    print("Gerando dashboard_ceo.html...")
    dados = {"imersoes": imersoes, "tipos": tipos,
             "desperdicio": desperdicio, "publicos": publicos}
    html = gerar_html(kpis, insights, dados)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] {OUTPUT_HTML.name} gerado")
    print(f"\n  KPIs:")
    for k in ["gasto_total","compras_totais","cpv_medio","roas_direto",
              "roas_mentoria","receita_projetada","total_leads","desperdicio"]:
        print(f"    {k:22s} = {kpis[k]}")
    print("\nAbra dashboard_ceo.html no navegador.")


if __name__ == "__main__":
    main()
