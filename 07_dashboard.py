"""
07_dashboard.py
Consolida CSVs dos scripts 01-06 e gera dashboard.html interativo com Chart.js.

CSVs esperados (gerados pelos scripts anteriores):
  campanhas.csv      — campanha, gasto, impressoes, cliques, ctr, cpv, conversoes
  cpv_diario.csv     — data, cpv
  posicionamentos.csv— posicionamento, gasto, impressoes
  idade_genero.csv   — idade, genero, gasto
  horarios.csv       — hora, cliques, impressoes, gasto
  funil.csv          — estagio, quantidade

Se algum CSV não for encontrado, dados de amostra são usados automaticamente.
"""

import json
import os
from pathlib import Path

# Tenta importar pandas; se não estiver instalado, usa dados de amostra.
try:
    import pandas as pd
    PANDAS_OK = True
except ImportError:
    PANDAS_OK = False
    print("[AVISO] pandas não instalado. Use: pip install pandas")
    print("[INFO]  Usando dados de amostra para todos os gráficos.\n")

BASE_DIR = Path(__file__).parent


# ─────────────────────────────────────────────
# LOADERS — tentam ler CSV, retornam fallback
# ─────────────────────────────────────────────

def _csv(nome):
    p = BASE_DIR / nome
    if PANDAS_OK and p.exists():
        return pd.read_csv(p)
    return None


def load_campanhas():
    df = _csv("campanhas.csv")
    if df is not None:
        cols = {"campanha": "campanha", "gasto": "gasto", "impressoes": "impressoes",
                "cliques": "cliques", "ctr": "ctr", "cpv": "cpv", "conversoes": "conversoes"}
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    # fallback
    import pandas as pd
    return pd.DataFrame({
        "campanha":   ["Remarketing Q1", "Prospecting BR", "Video Views", "Lead Gen", "Brand Awareness"],
        "gasto":      [12400, 9800, 7300, 15200, 5600],
        "impressoes": [480000, 620000, 890000, 310000, 740000],
        "cliques":    [9200, 6800, 4100, 12400, 3200],
        "ctr":        [1.92, 1.10, 0.46, 4.00, 0.43],
        "cpv":        [0.026, 0.016, 0.008, 0.049, 0.008],
        "conversoes": [340, 210, 95, 520, 88],
    })


def load_cpv_diario():
    df = _csv("cpv_diario.csv")
    if df is not None:
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    import pandas as pd
    datas = [f"2024-{m:02d}-{d:02d}"
             for m in range(1, 4) for d in [1, 8, 15, 22]]
    import random; random.seed(42)
    cpvs = [round(0.02 + random.gauss(0, 0.005), 4) for _ in datas]
    return pd.DataFrame({"data": datas, "cpv": cpvs})


def load_posicionamentos():
    df = _csv("posicionamentos.csv")
    if df is not None:
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    import pandas as pd
    return pd.DataFrame({
        "posicionamento": ["Feed Mobile", "Feed Desktop", "Stories", "Reels", "Audience Network", "Messenger"],
        "gasto":          [18400, 11200, 8700, 6300, 3800, 2100],
        "impressoes":     [620000, 380000, 290000, 210000, 180000, 95000],
    })


def load_idade_genero():
    df = _csv("idade_genero.csv")
    if df is not None:
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    import pandas as pd
    idades  = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    generos = ["Masculino", "Feminino"]
    rows = []
    gastos = {
        ("18-24","Masculino"):4200, ("18-24","Feminino"):5100,
        ("25-34","Masculino"):8700, ("25-34","Feminino"):9400,
        ("35-44","Masculino"):7200, ("35-44","Feminino"):6800,
        ("45-54","Masculino"):4100, ("45-54","Feminino"):3900,
        ("55-64","Masculino"):2300, ("55-64","Feminino"):2100,
        ("65+",  "Masculino"):1100, ("65+",  "Feminino"):900,
    }
    for i in idades:
        for g in generos:
            rows.append({"idade": i, "genero": g, "gasto": gastos[(i, g)]})
    return pd.DataFrame(rows)


def load_horarios():
    df = _csv("horarios.csv")
    if df is not None:
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    import pandas as pd
    horas   = list(range(24))
    cliques = [120,80,60,45,55,110,280,540,720,810,890,950,
               870,820,760,830,950,1020,980,880,740,620,430,260]
    return pd.DataFrame({"hora": horas, "cliques": cliques})


def load_funil():
    df = _csv("funil.csv")
    if df is not None:
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    import pandas as pd
    return pd.DataFrame({
        "estagio":    ["Impressões", "Alcance", "Cliques", "Visualizações de página", "Leads", "Conversões"],
        "quantidade": [3040000, 1820000, 35700, 18400, 2800, 1253],
    })


# ─────────────────────────────────────────────
# KPIs globais
# ─────────────────────────────────────────────

def calcular_kpis(df_camp):
    gasto      = df_camp["gasto"].sum()
    impressoes = df_camp["impressoes"].sum()
    ctr        = df_camp["ctr"].mean() if "ctr" in df_camp else (df_camp["cliques"].sum() / impressoes * 100)
    cpv        = df_camp["cpv"].mean() if "cpv" in df_camp else (gasto / impressoes)
    return {
        "gasto_total": f"R$ {gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "impressoes":  f"{impressoes:,}".replace(",", "."),
        "ctr_medio":   f"{ctr:.2f}%",
        "cpv_medio":   f"R$ {cpv:.4f}",
    }


# ─────────────────────────────────────────────
# HTML TEMPLATE
# ─────────────────────────────────────────────

def gerar_html(kpis, dados):
    camp      = dados["campanhas"]
    cpv_dia   = dados["cpv_diario"]
    posic     = dados["posicionamentos"]
    ig        = dados["idade_genero"]
    hor       = dados["horarios"]
    funil     = dados["funil"]

    # ── Scatter: CTR vs CPV ──────────────────
    scatter_pts = [{"x": round(float(r["ctr"]), 3),
                    "y": round(float(r["cpv"]), 5),
                    "label": r["campanha"]}
                   for _, r in camp.iterrows()]

    # ── Heatmap Idade × Gênero ───────────────
    idades  = ig["idade"].unique().tolist()
    generos = ig["genero"].unique().tolist()
    heatmap_datasets = []
    palette_hm = ["#6366f1", "#ec4899"]
    for gi, gen in enumerate(generos):
        sub = ig[ig["genero"] == gen].set_index("idade")
        heatmap_datasets.append({
            "label": gen,
            "data":  [float(sub.loc[i, "gasto"]) if i in sub.index else 0 for i in idades],
            "backgroundColor": palette_hm[gi % len(palette_hm)] + "cc",
            "borderColor":     palette_hm[gi % len(palette_hm)],
            "borderWidth": 1,
        })

    # ── Funil ────────────────────────────────
    funil_labels = funil["estagio"].tolist()
    funil_valores = [int(v) for v in funil["quantidade"].tolist()]
    funil_max = funil_valores[0] if funil_valores else 1
    funil_pcts = [round(v / funil_max * 100, 1) for v in funil_valores]

    # ── Cores padrão ─────────────────────────
    cores_bar  = ["#6366f1","#8b5cf6","#a78bfa","#c4b5fd","#ddd6fe"]
    cores_pie  = ["#6366f1","#8b5cf6","#ec4899","#f59e0b","#10b981","#06b6d4"]

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Facebook Ads — Dashboard de Performance</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: #0f0f1a;
    color: #e2e8f0;
    font-family: 'Segoe UI', system-ui, sans-serif;
    min-height: 100vh;
    padding: 2rem;
  }}

  header {{
    text-align: center;
    margin-bottom: 2.5rem;
  }}
  header h1 {{
    font-size: 2rem;
    background: linear-gradient(135deg, #6366f1, #a78bfa, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    letter-spacing: -0.5px;
  }}
  header p {{
    color: #94a3b8;
    margin-top: .4rem;
    font-size: .95rem;
  }}

  /* ── KPI Cards ── */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.2rem;
    margin-bottom: 2.5rem;
  }}
  .kpi-card {{
    background: linear-gradient(135deg, rgba(99,102,241,.15), rgba(139,92,246,.08));
    border: 1px solid rgba(99,102,241,.3);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    position: relative;
    overflow: hidden;
    transition: transform .2s, box-shadow .2s;
  }}
  .kpi-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(99,102,241,.25);
  }}
  .kpi-card::before {{
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 100px; height: 100px;
    background: radial-gradient(circle, rgba(99,102,241,.2), transparent 70%);
    border-radius: 50%;
  }}
  .kpi-label {{ font-size: .8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }}
  .kpi-value {{ font-size: 1.9rem; font-weight: 700; margin-top: .4rem; color: #f1f5f9; }}
  .kpi-icon  {{ position: absolute; top: 1rem; right: 1.2rem; font-size: 1.6rem; opacity: .5; }}

  /* ── Chart Grid ── */
  .charts-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }}
  .chart-card {{
    background: rgba(15,15,30,.8);
    border: 1px solid rgba(99,102,241,.2);
    border-radius: 16px;
    padding: 1.5rem;
    position: relative;
  }}
  .chart-card.full-width {{ grid-column: 1 / -1; }}
  .chart-card h2 {{
    font-size: .9rem;
    font-weight: 600;
    color: #a78bfa;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: .5px;
  }}
  canvas {{ max-height: 320px; }}

  /* ── Funil Custom ── */
  .funil-container {{
    display: flex;
    flex-direction: column;
    gap: .6rem;
    padding: .5rem 0;
  }}
  .funil-row {{ display: flex; align-items: center; gap: 1rem; }}
  .funil-label {{
    width: 180px;
    font-size: .82rem;
    color: #cbd5e1;
    text-align: right;
    flex-shrink: 0;
  }}
  .funil-bar-wrap {{
    flex: 1;
    height: 34px;
    background: rgba(255,255,255,.05);
    border-radius: 6px;
    overflow: hidden;
    display: flex;
    align-items: center;
  }}
  .funil-bar {{
    height: 100%;
    border-radius: 6px;
    display: flex;
    align-items: center;
    padding-left: .7rem;
    font-size: .8rem;
    font-weight: 600;
    color: #fff;
    transition: width .8s ease;
  }}
  .funil-val {{
    width: 110px;
    text-align: right;
    font-size: .8rem;
    color: #94a3b8;
    flex-shrink: 0;
  }}

  @media (max-width: 768px) {{
    .charts-grid {{ grid-template-columns: 1fr; }}
    .chart-card.full-width {{ grid-column: 1; }}
    .kpi-value {{ font-size: 1.5rem; }}
  }}
</style>
</head>
<body>

<header>
  <h1>Facebook Ads — Dashboard de Performance</h1>
  <p>Análise consolidada · Gerado automaticamente por 07_dashboard.py</p>
</header>

<!-- KPI Cards -->
<div class="kpi-grid">
  <div class="kpi-card">
    <span class="kpi-icon">💸</span>
    <div class="kpi-label">Gasto Total</div>
    <div class="kpi-value">{kpis["gasto_total"]}</div>
  </div>
  <div class="kpi-card">
    <span class="kpi-icon">👁️</span>
    <div class="kpi-label">Impressões</div>
    <div class="kpi-value">{kpis["impressoes"]}</div>
  </div>
  <div class="kpi-card">
    <span class="kpi-icon">🖱️</span>
    <div class="kpi-label">CTR Médio</div>
    <div class="kpi-value">{kpis["ctr_medio"]}</div>
  </div>
  <div class="kpi-card">
    <span class="kpi-icon">📹</span>
    <div class="kpi-label">CPV Médio</div>
    <div class="kpi-value">{kpis["cpv_medio"]}</div>
  </div>
</div>

<!-- Charts Grid -->
<div class="charts-grid">

  <!-- 1. Gasto por Campanha -->
  <div class="chart-card">
    <h2>💰 Gasto por Campanha</h2>
    <canvas id="chartCampanhas"></canvas>
  </div>

  <!-- 2. Evolução do CPV -->
  <div class="chart-card">
    <h2>📈 Evolução do CPV</h2>
    <canvas id="chartCpv"></canvas>
  </div>

  <!-- 3. Distribuição por Posicionamento -->
  <div class="chart-card">
    <h2>🥧 Distribuição por Posicionamento</h2>
    <canvas id="chartPosic"></canvas>
  </div>

  <!-- 4. Heatmap: Idade × Gênero -->
  <div class="chart-card">
    <h2>🌡️ Gasto: Idade × Gênero</h2>
    <canvas id="chartIdadeGenero"></canvas>
  </div>

  <!-- 5. Performance por Horário -->
  <div class="chart-card full-width">
    <h2>🕐 Cliques por Horário do Dia</h2>
    <canvas id="chartHorario"></canvas>
  </div>

  <!-- 6. Funil de Conversão -->
  <div class="chart-card full-width">
    <h2>🔻 Funil de Conversão</h2>
    <div class="funil-container" id="funil"></div>
  </div>

  <!-- 7. Scatter: CTR vs CPV -->
  <div class="chart-card full-width">
    <h2>🔵 CTR vs CPV por Campanha (Outliers)</h2>
    <canvas id="chartScatter"></canvas>
  </div>

</div>

<script>
// ── Configurações globais Chart.js ────────────────────────────
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";

const GRAD = (ctx, c1, c2) => {{
  const g = ctx.createLinearGradient(0, 0, 0, 320);
  g.addColorStop(0, c1); g.addColorStop(1, c2);
  return g;
}};

// ── 1. Gasto por Campanha ─────────────────────────────────────
(function() {{
  const ctx = document.getElementById('chartCampanhas').getContext('2d');
  const labels = {json.dumps(camp["campanha"].tolist())};
  const data   = {json.dumps([float(v) for v in camp["gasto"].tolist()])};
  new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels,
      datasets: [{{
        label: 'Gasto (R$)',
        data,
        backgroundColor: {json.dumps(cores_bar[:len(camp)])},
        borderRadius: 8,
        borderSkipped: false,
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ grid: {{ display: false }} }},
        y: {{
          ticks: {{ callback: v => 'R$ ' + v.toLocaleString('pt-BR') }},
        }}
      }}
    }}
  }});
}})();

// ── 2. Evolução CPV ───────────────────────────────────────────
(function() {{
  const ctx = document.getElementById('chartCpv').getContext('2d');
  const grad = GRAD(ctx, 'rgba(99,102,241,.4)', 'rgba(99,102,241,0)');
  new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: {json.dumps(cpv_dia["data"].tolist())},
      datasets: [{{
        label: 'CPV (R$)',
        data:  {json.dumps([float(v) for v in cpv_dia["cpv"].tolist()])},
        borderColor: '#6366f1',
        backgroundColor: grad,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#6366f1',
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 8 }} }},
        y: {{ ticks: {{ callback: v => 'R$ ' + v.toFixed(4) }} }}
      }}
    }}
  }});
}})();

// ── 3. Distribuição por Posicionamento ────────────────────────
(function() {{
  const ctx = document.getElementById('chartPosic').getContext('2d');
  new Chart(ctx, {{
    type: 'doughnut',
    data: {{
      labels: {json.dumps(posic["posicionamento"].tolist())},
      datasets: [{{
        data:            {json.dumps([float(v) for v in posic["gasto"].tolist()])},
        backgroundColor: {json.dumps(cores_pie[:len(posic)])},
        borderWidth: 2,
        borderColor: '#0f0f1a',
        hoverOffset: 8,
      }}]
    }},
    options: {{
      responsive: true,
      cutout: '60%',
      plugins: {{
        legend: {{ position: 'right', labels: {{ boxWidth: 12, padding: 12 }} }}
      }}
    }}
  }});
}})();

// ── 4. Heatmap Idade × Gênero (grouped bar) ───────────────────
(function() {{
  const ctx = document.getElementById('chartIdadeGenero').getContext('2d');
  new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: {json.dumps(idades)},
      datasets: {json.dumps(heatmap_datasets)}
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ position: 'top' }} }},
      scales: {{
        x: {{ grid: {{ display: false }} }},
        y: {{ ticks: {{ callback: v => 'R$ ' + v.toLocaleString('pt-BR') }} }}
      }}
    }}
  }});
}})();

// ── 5. Performance por Horário ────────────────────────────────
(function() {{
  const ctx   = document.getElementById('chartHorario').getContext('2d');
  const horas = {json.dumps(hor["hora"].tolist())};
  const cliques = {json.dumps([int(v) for v in hor["cliques"].tolist()])};
  const maxVal  = Math.max(...cliques);
  const bgColors = cliques.map(v => {{
    const ratio = v / maxVal;
    return `rgba(${{Math.round(99 + (236-99)*ratio)}}, ${{Math.round(102 + (73-102)*ratio)}}, ${{Math.round(241 + (153-241)*ratio)}}, 0.85)`;
  }});
  new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: horas.map(h => h + 'h'),
      datasets: [{{
        label: 'Cliques',
        data: cliques,
        backgroundColor: bgColors,
        borderRadius: 5,
        borderSkipped: false,
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ grid: {{ display: false }} }},
        y: {{ grid: {{ color: 'rgba(255,255,255,.05)' }} }}
      }}
    }}
  }});
}})();

// ── 6. Funil (HTML customizado) ───────────────────────────────
(function() {{
  const labels  = {json.dumps(funil_labels)};
  const valores = {json.dumps(funil_valores)};
  const pcts    = {json.dumps(funil_pcts)};
  const cores   = ['#6366f1','#7c3aed','#9333ea','#a855f7','#c084fc','#e879f9'];
  const el = document.getElementById('funil');
  labels.forEach((lbl, i) => {{
    const row = document.createElement('div');
    row.className = 'funil-row';
    row.innerHTML = `
      <div class="funil-label">${{lbl}}</div>
      <div class="funil-bar-wrap">
        <div class="funil-bar" style="width:${{pcts[i]}}%; background:${{cores[i]}};">
          ${{pcts[i]}}%
        </div>
      </div>
      <div class="funil-val">${{valores[i].toLocaleString('pt-BR')}}</div>
    `;
    el.appendChild(row);
  }});
}})();

// ── 7. Scatter CTR vs CPV ─────────────────────────────────────
(function() {{
  const ctx = document.getElementById('chartScatter').getContext('2d');
  const pts = {json.dumps(scatter_pts)};
  new Chart(ctx, {{
    type: 'scatter',
    data: {{
      datasets: [{{
        label: 'Campanhas',
        data: pts,
        backgroundColor: pts.map((_, i) => {json.dumps(cores_pie)}[i % {len(cores_pie)}] + 'cc'),
        pointRadius: 10,
        pointHoverRadius: 14,
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          callbacks: {{
            label: ctx => {{
              const p = ctx.raw;
              return ` ${{p.label}}: CTR ${{p.x}}% | CPV R$ ${{p.y}}`;
            }}
          }}
        }}
      }},
      scales: {{
        x: {{
          title: {{ display: true, text: 'CTR (%)', color: '#94a3b8' }},
          grid: {{ color: 'rgba(255,255,255,.05)' }}
        }},
        y: {{
          title: {{ display: true, text: 'CPV (R$)', color: '#94a3b8' }},
          grid: {{ color: 'rgba(255,255,255,.05)' }},
          ticks: {{ callback: v => 'R$ ' + v.toFixed(4) }}
        }}
      }}
    }}
  }});
}})();

</script>
</body>
</html>"""
    return html


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    if not PANDAS_OK:
        # Se pandas não está disponível, importa aqui só para amostra
        try:
            import pandas as pd
        except ImportError:
            print("[ERRO] Instale pandas: pip install pandas")
            return

    print("Carregando dados...")
    camp  = load_campanhas()
    cpv   = load_cpv_diario()
    posic = load_posicionamentos()
    ig    = load_idade_genero()
    hor   = load_horarios()
    fun   = load_funil()

    print("Calculando KPIs...")
    kpis = calcular_kpis(camp)

    print("Gerando dashboard.html...")
    dados = {
        "campanhas":     camp,
        "cpv_diario":    cpv,
        "posicionamentos": posic,
        "idade_genero":  ig,
        "horarios":      hor,
        "funil":         fun,
    }
    html = gerar_html(kpis, dados)

    saida = BASE_DIR / "dashboard.html"
    with open(saida, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n[OK] dashboard.html gerado em: {saida}")
    print(f"  KPIs consolidados:")
    for k, v in kpis.items():
        print(f"    {k:15s} = {v}")
    print("\nAbra dashboard.html no navegador para visualizar.")


if __name__ == "__main__":
    main()
