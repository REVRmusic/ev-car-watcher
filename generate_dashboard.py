#!/usr/bin/env python3
"""
Générateur de tableau de bord HTML haut de gamme pour la veille des véhicules électriques.
Design moderne, épuré, responsive, avec observatoire des décotes et courbes prévisionnelles Chart.js.
"""

import json
from datetime import datetime

def build_html(results_data, config):
    listings = results_data.get("listings", [])
    financial = config.get("financial", {})
    criteria = config.get("criteria", {})
    trends = results_data.get("trends", {})
    stats_by_model = trends.get("stats_by_model", {})
    budget_ceiling = trends.get("budget_ceiling_vehicle", 25631.14)
    
    generated_at = datetime.fromisoformat(results_data.get("generated_at", datetime.now().isoformat())).strftime("%d/%m/%Y à %H:%M")
    
    total_listings = len(listings)
    in_budget_count = results_data.get("in_budget_count", 0)
    negotiable_count = results_data.get("negotiable_count", 0)
    new_count = results_data.get("new_count", 0)
    price_drop_count = results_data.get("price_drop_count", 0)
    sweet_spot_count = len([x for x in listings if x.get("is_sweet_spot") and x.get("budget_status") in ["EXCELLENT_DEAL", "WITHIN_BUDGET"]])

    # Données JSON pour les scripts clients (annonces et statistiques prévisionnelles)
    listings_json = json.dumps(listings, ensure_ascii=False)
    trends_json = json.dumps(trends, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="fr" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Observatoire & Veille Véhicules Électriques — Décote & Prévisions</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
      --bg-primary: #0b0f19;
      --bg-secondary: #111827;
      --bg-card: #161f30;
      --bg-card-hover: #1c273c;
      --border-color: #243046;
      --border-highlight: #3b82f6;
      --text-primary: #f3f4f6;
      --text-secondary: #9ca3af;
      --text-muted: #6b7280;
      --accent-blue: #3b82f6;
      --accent-blue-soft: rgba(59, 130, 246, 0.15);
      --accent-emerald: #10b981;
      --accent-emerald-soft: rgba(16, 185, 129, 0.15);
      --accent-cyan: #06b6d4;
      --accent-cyan-soft: rgba(6, 182, 212, 0.15);
      --accent-amber: #f59e0b;
      --accent-amber-soft: rgba(245, 158, 11, 0.15);
      --accent-rose: #ef4444;
      --accent-rose-soft: rgba(239, 68, 68, 0.15);
      --accent-purple: #8b5cf6;
      --accent-purple-soft: rgba(139, 92, 246, 0.15);
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.4);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.4);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.5;
      min-height: 100vh;
      padding: 2rem 1.5rem 5rem;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
    }}

    /* HEADER */
    header {{
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      margin-bottom: 2.5rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 2rem;
    }}

    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 1.5rem;
    }}

    .title-group h1 {{
      font-size: 2rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .title-group p {{
      color: var(--text-secondary);
      font-size: 0.95rem;
      margin-top: 0.35rem;
    }}

    .meta-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background-color: var(--bg-secondary);
      border: 1px solid var(--border-color);
      padding: 0.5rem 1rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-secondary);
    }}

    .meta-badge .dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--accent-emerald);
      box-shadow: 0 0 10px var(--accent-emerald);
      animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
      0% {{ transform: scale(0.95); opacity: 0.8; }}
      50% {{ transform: scale(1.15); opacity: 1; }}
      100% {{ transform: scale(0.95); opacity: 0.8; }}
    }}

    /* BANDEAU SIMULATION FINANCIÈRE */
    .financial-banner {{
      background: linear-gradient(135deg, rgba(30, 58, 138, 0.25) 0%, rgba(17, 24, 39, 0.6) 100%);
      border: 1px solid rgba(59, 130, 246, 0.3);
      border-radius: 1rem;
      padding: 1.25rem 1.5rem;
      margin-bottom: 2rem;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1.25rem;
    }}

    .financial-details {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 2rem;
    }}

    .fin-item {{
      display: flex;
      flex-direction: column;
    }}

    .fin-item span:first-child {{
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
    }}

    .fin-item span:last-child {{
      font-size: 1.05rem;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      color: #93c5fd;
    }}

    /* STATS / KPI GRID */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2.5rem;
    }}

    .kpi-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 1rem;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(59, 130, 246, 0.4);
    }}

    .kpi-card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--accent-blue), transparent);
    }}

    .kpi-card.cyan::before {{ background: linear-gradient(90deg, var(--accent-cyan), transparent); }}
    .kpi-card.emerald::before {{ background: linear-gradient(90deg, var(--accent-emerald), transparent); }}
    .kpi-card.amber::before {{ background: linear-gradient(90deg, var(--accent-amber), transparent); }}

    .kpi-label {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      font-weight: 600;
    }}

    .kpi-value {{
      font-size: 1.85rem;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-primary);
    }}

    .kpi-subtext {{
      font-size: 0.8rem;
      color: var(--text-secondary);
    }}

    /* SECTION OBSERVATOIRE DÉCOTE */
    .observatory-section {{
      background-color: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 1.25rem;
      padding: 1.75rem;
      margin-bottom: 3rem;
      display: flex;
      flex-direction: column;
      gap: 1.75rem;
    }}

    .section-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      flex-wrap: wrap;
      gap: 1rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 1rem;
    }}

    .section-title {{
      font-size: 1.35rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }}

    .section-subtitle {{
      font-size: 0.85rem;
      color: var(--text-secondary);
      margin-top: 0.2rem;
    }}

    /* TABLEAU DES FOURCHETTES */
    .table-container {{
      width: 100%;
      overflow-x: auto;
      border-radius: 0.75rem;
      border: 1px solid var(--border-color);
      background-color: var(--bg-card);
    }}

    table.trends-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.875rem;
    }}

    table.trends-table th {{
      background-color: rgba(15, 23, 42, 0.75);
      padding: 0.85rem 1rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      border-bottom: 1px solid var(--border-color);
    }}

    table.trends-table td {{
      padding: 0.9rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      color: var(--text-primary);
    }}

    table.trends-table tr:hover td {{
      background-color: rgba(59, 130, 246, 0.04);
    }}

    .cell-model {{
      font-weight: 700;
      color: #ffffff;
    }}

    .cell-mono {{
      font-family: 'JetBrains Mono', monospace;
    }}

    .tag-horizon {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.25rem 0.65rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 700;
    }}

    .tag-horizon.success {{
      background-color: var(--accent-emerald-soft);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}

    .tag-horizon.warning {{
      background-color: var(--accent-amber-soft);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }}

    .tag-horizon.info {{
      background-color: var(--accent-blue-soft);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }}

    .tag-horizon.secondary {{
      background-color: rgba(156, 163, 175, 0.1);
      color: #9ca3af;
      border: 1px solid rgba(156, 163, 175, 0.2);
    }}

    /* GRAPHIQUES GRID */
    .charts-grid {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 1.5rem;
    }}

    @media (max-width: 1024px) {{
      .charts-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .chart-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 1rem;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .chart-title {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .chart-legend-hint {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 500;
    }}

    .chart-canvas-wrap {{
      position: relative;
      height: 340px;
      width: 100%;
    }}

    /* CONTROLS & FILTERS */
    .controls-panel {{
      background-color: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 1rem;
      padding: 1.25rem;
      margin-bottom: 2rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .filter-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      align-items: center;
    }}

    .filter-label {{
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-right: 0.5rem;
    }}

    .filter-btn {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      padding: 0.45rem 0.9rem;
      border-radius: 0.5rem;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .filter-btn:hover {{
      background-color: var(--bg-card-hover);
      color: var(--text-primary);
      border-color: var(--border-highlight);
    }}

    .filter-btn.active {{
      background-color: var(--accent-blue);
      color: #ffffff;
      border-color: var(--accent-blue);
      font-weight: 600;
    }}

    .filter-btn.sweet-btn.active {{
      background-color: var(--accent-cyan);
      border-color: var(--accent-cyan);
    }}

    /* GRID OF CARS */
    .cars-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 1.5rem;
    }}

    .car-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 1rem;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: all 0.25s ease;
      position: relative;
    }}

    .car-card:hover {{
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg);
      border-color: rgba(59, 130, 246, 0.4);
    }}

    .car-card.sweet-card {{
      border-color: rgba(6, 182, 212, 0.4);
    }}

    .car-card.sweet-card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, var(--accent-cyan), var(--accent-emerald));
      z-index: 2;
    }}

    .card-image-wrap {{
      position: relative;
      width: 100%;
      height: 220px;
      background-color: #0f172a;
      overflow: hidden;
    }}

    .card-image {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s ease;
    }}

    .car-card:hover .card-image {{
      transform: scale(1.05);
    }}

    .image-overlay-badges {{
      position: absolute;
      top: 0.75rem;
      left: 0.75rem;
      right: 0.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      pointer-events: none;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.3rem 0.65rem;
      border-radius: 0.4rem;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: uppercase;
      backdrop-filter: blur(8px);
      box-shadow: var(--shadow-sm);
    }}

    .badge-success {{
      background-color: rgba(16, 185, 129, 0.85);
      color: #ffffff;
      border: 1px solid #10b981;
    }}

    .badge-info {{
      background-color: rgba(59, 130, 246, 0.85);
      color: #ffffff;
      border: 1px solid #3b82f6;
    }}

    .badge-warning {{
      background-color: rgba(245, 158, 11, 0.85);
      color: #ffffff;
      border: 1px solid #f59e0b;
    }}

    .badge-danger {{
      background-color: rgba(239, 68, 68, 0.85);
      color: #ffffff;
      border: 1px solid #ef4444;
    }}

    .score-badge {{
      background-color: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #f8fafc;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      font-weight: 700;
    }}

    .card-body {{
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      flex: 1;
      gap: 1rem;
    }}

    .car-header {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}

    .car-model-name {{
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--accent-blue);
    }}

    .car-title {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-primary);
      line-height: 1.35;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    /* FINANCIAL HIGHLIGHT BOX */
    .fin-box {{
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--border-color);
      border-radius: 0.75rem;
      padding: 0.9rem;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
    }}

    .fin-box-item {{
      display: flex;
      flex-direction: column;
    }}

    .fin-box-label {{
      font-size: 0.7rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
    }}

    .fin-box-val {{
      font-size: 1.15rem;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
    }}

    .fin-box-val.target-ok {{
      color: var(--accent-emerald);
    }}

    .fin-box-val.target-mid {{
      color: #60a5fa;
    }}

    .fin-box-val.target-warn {{
      color: var(--accent-amber);
    }}

    .price-tag {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      padding-bottom: 0.5rem;
      border-bottom: 1px dashed var(--border-color);
    }}

    .price-value {{
      font-size: 1.5rem;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      color: #ffffff;
    }}

    .price-sub {{
      font-size: 0.8rem;
      color: var(--text-secondary);
    }}

    /* DETAILS CHIPS */
    .chips-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
    }}

    .chip {{
      background-color: var(--bg-secondary);
      border: 1px solid var(--border-color);
      padding: 0.25rem 0.55rem;
      border-radius: 0.4rem;
      font-size: 0.8rem;
      color: var(--text-secondary);
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
    }}

    .card-footer {{
      margin-top: auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 0.75rem;
      border-top: 1px solid var(--border-color);
    }}

    .location-info {{
      font-size: 0.8rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .btn-view {{
      background-color: var(--accent-blue);
      color: #ffffff;
      padding: 0.55rem 1rem;
      border-radius: 0.5rem;
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 600;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .btn-view:hover {{
      background-color: #2563eb;
      transform: translateY(-1px);
    }}

    .empty-state {{
      grid-column: 1 / -1;
      background-color: var(--bg-card);
      border: 1px dashed var(--border-color);
      border-radius: 1rem;
      padding: 4rem 2rem;
      text-align: center;
      color: var(--text-secondary);
    }}
  </style>
</head>
<body>
  <div class="container">
    
    <!-- HEADER -->
    <header>
      <div class="header-top">
        <div class="title-group">
          <h1>⚡ Surveillance Marché Véhicules Électriques</h1>
          <p>Observatoire des prix, courbes prévisionnelles de décote & alertes d'opportunités</p>
        </div>
        <div class="meta-badge">
          <span class="dot"></span>
          <span>Dernière analyse : {generated_at}</span>
        </div>
      </div>

      <!-- BANDEAU SIMULATION FINANCIÈRE BOURSOBANK -->
      <div class="financial-banner">
        <div class="financial-details">
          <div class="fin-item">
            <span>Barème Financement</span>
            <span>BoursoBank Véhicule Propre (4,35 % TAEG fixe)</span>
          </div>
          <div class="fin-item">
            <span>Durée</span>
            <span>72 mois (6 ans)</span>
          </div>
          <div class="fin-item">
            <span>Mensualité Cible</span>
            <span>≤ 300 € / mois</span>
          </div>
          <div class="fin-item">
            <span>Apport Net</span>
            <span>5 000 € à 7 000 €</span>
          </div>
          <div class="fin-item">
            <span>Plafond Véhicule Net</span>
            <span style="color:#34d399">~{budget_ceiling:,.0f} €</span>
          </div>
          <div class="fin-item">
            <span>Règle Année & Km</span>
            <span style="color:#67e8f9">2023-2025 | ≤ 100k km (Idéal 50k-60k km)</span>
          </div>
        </div>
      </div>

      <!-- KPI METRICS -->
      <div class="kpi-grid">
        <div class="kpi-card emerald">
          <span class="kpi-label">Dans le budget (≤ 300€/m)</span>
          <span class="kpi-value">{in_budget_count}</span>
          <span class="kpi-subtext">Directement finançables</span>
        </div>
        <div class="kpi-card cyan">
          <span class="kpi-label">🎯 Cibles Idéales (2023+ & ≤ 60k km)</span>
          <span class="kpi-value">{sweet_spot_count}</span>
          <span class="kpi-subtext">Dans le budget & critères parfaits</span>
        </div>
        <div class="kpi-card amber">
          <span class="kpi-label">Opportunités à négocier</span>
          <span class="kpi-value">{negotiable_count}</span>
          <span class="kpi-subtext">Dépassement &lt; 25 €/mois</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Total annonces qualifiées</span>
          <span class="kpi-value">{total_listings}</span>
          <span class="kpi-subtext">Exclusion stricte &gt; 100k km</span>
        </div>
      </div>
    </header>

    <!-- OBSERVATOIRE DES PRIX & COURBES DE DÉCOTE -->
    <section class="observatory-section">
      <div class="section-header">
        <div>
          <h2 class="section-title">📊 Observatoire de Marché & Prévision de Décote</h2>
          <p class="section-subtitle">Suivi des fourchettes de prix en temps réel et projections mathématiques vers votre budget cible ({budget_ceiling:,.0f} € net)</p>
        </div>
      </div>

      <!-- TABLEAU DES FOURCHETTES PAR MODÈLE -->
      <div class="table-container">
        <table class="trends-table">
          <thead>
            <tr>
              <th>Modèle surveillé</th>
              <th>Annonces</th>
              <th>Prix Min</th>
              <th>Prix Médian</th>
              <th>Prix Max</th>
              <th>Mensualité Min (Apport 7k€)</th>
              <th>Horizon Budget BoursoBank</th>
            </tr>
          </thead>
          <tbody>
"""

    for m_id, stats in stats_by_model.items():
        min_p = f"{stats['min_price']:,} €".replace(",", " ")
        med_p = f"{stats['median_price']:,} €".replace(",", " ")
        max_p = f"{stats['max_price']:,} €".replace(",", " ")
        mens_min = f"{stats['min_mens_7k']} €/m"
        horizon = stats['budget_horizon']
        h_class = stats['horizon_class']

        html += f"""
            <tr>
              <td class="cell-model">{stats['model_name']}</td>
              <td class="cell-mono">{stats['count']}</td>
              <td class="cell-mono" style="color:#34d399; font-weight:700;">{min_p}</td>
              <td class="cell-mono">{med_p}</td>
              <td class="cell-mono" style="color:#94a3b8;">{max_p}</td>
              <td class="cell-mono" style="font-weight:700; color:#93c5fd;">{mens_min}</td>
              <td><span class="tag-horizon {h_class}">{horizon}</span></td>
            </tr>
        """

    html += f"""
          </tbody>
        </table>
      </div>

      <!-- GRAPHIQUES INTERACTIFS -->
      <div class="charts-grid">
        <!-- COURBE PRÉVISIONNELLE -->
        <div class="chart-card">
          <div class="chart-title">
            <span>📈 Courbes Prévisionnelles de Décote (Projection 24 Mois)</span>
            <span class="chart-legend-hint">Cliquez sur un modèle pour filtrer</span>
          </div>
          <div class="chart-canvas-wrap">
            <canvas id="depreciationChart"></canvas>
          </div>
        </div>

        <!-- POSITIONNEMENT ACTUEL PAR MODÈLE -->
        <div class="chart-card">
          <div class="chart-title">
            <span>⚖️ Prix Minimum Actuel vs Plafond Budget</span>
          </div>
          <div class="chart-canvas-wrap">
            <canvas id="budgetComparisonChart"></canvas>
          </div>
        </div>
      </div>
    </section>

    <!-- FILTRES INTERACTIFS -->
    <div class="controls-panel">
      <div class="filter-row">
        <span class="filter-label">Filtres :</span>
        <button class="filter-btn active" data-filter-type="budget" data-val="all">Tous les résultats</button>
        <button class="filter-btn sweet-btn" data-filter-type="budget" data-val="sweet_spot" style="color:#22d3ee; border-color:rgba(6,182,212,0.4)">🎯 Cible Idéale (2023+ & ≤ 60k km)</button>
        <button class="filter-btn" data-filter-type="budget" data-val="budget_ok">Dans le budget (≤ 300€/m)</button>
        <button class="filter-btn" data-filter-type="budget" data-val="pepite">Top Pépites (Score ≥ 8.0)</button>
        <button class="filter-btn" data-filter-type="budget" data-val="negotiable">À négocier</button>
      </div>

      <div class="filter-row" style="margin-top: 0.5rem;">
        <span class="filter-label">Modèle :</span>
        <button class="filter-btn active" data-filter-type="model" data-val="all">Tous ({total_listings})</button>
        <button class="filter-btn" data-filter-type="model" data-val="megane_etech_iconic">Mégane E-Tech</button>
        <button class="filter-btn" data-filter-type="model" data-val="skoda_enyaq_80">Skoda Enyaq 80</button>
        <button class="filter-btn" data-filter-type="model" data-val="hyundai_ioniq_5">Ioniq 5</button>
        <button class="filter-btn" data-filter-type="model" data-val="kia_ev6">Kia EV6</button>
        <button class="filter-btn" data-filter-type="model" data-val="kia_niro_ev_premium">Kia Niro EV</button>
        <button class="filter-btn" data-filter-type="model" data-val="mustang_mache_er">Mustang Mach-E</button>
        <button class="filter-btn" data-filter-type="model" data-val="hyundai_kona_2_exec">Kona 2 Executive</button>
        <button class="filter-btn" data-filter-type="model" data-val="peugeot_e3008_gt">Peugeot e-3008 GT</button>
        <button class="filter-btn" data-filter-type="model" data-val="byd_seal_u_design">BYD Seal U</button>
      </div>
    </div>

    <!-- GRILLE DES VÉHICULES -->
    <div class="cars-grid" id="cars-grid">
      <!-- Les cartes seront injectées dynamiquement par JS -->
    </div>

  </div>

  <script>
    const listingsData = {listings_json};
    const trendsData = {trends_json};
    let currentBudgetFilter = 'all';
    let currentModelFilter = 'all';

    function renderListings() {{
      const container = document.getElementById('cars-grid');
      container.innerHTML = '';

      const filtered = listingsData.filter(item => {{
        // Filtre Modèle
        if (currentModelFilter !== 'all' && item.model_id !== currentModelFilter) {{
          return false;
        }}
        // Filtres Spécifiques
        if (currentBudgetFilter === 'sweet_spot') {{
          return item.is_sweet_spot && (item.budget_status === 'EXCELLENT_DEAL' || item.budget_status === 'WITHIN_BUDGET');
        }} else if (currentBudgetFilter === 'budget_ok') {{
          return item.budget_status === 'EXCELLENT_DEAL' || item.budget_status === 'WITHIN_BUDGET';
        }} else if (currentBudgetFilter === 'negotiable') {{
          return item.budget_status === 'NEGOTIABLE';
        }} else if (currentBudgetFilter === 'pepite') {{
          return item.score >= 8.0;
        }}
        return true;
      }});

      if (filtered.length === 0) {{
        container.innerHTML = `
          <div class="empty-state">
            <h3>Aucune offre ne correspond aux critères sélectionnés</h3>
            <p style="margin-top: 0.5rem;">Modifiez vos filtres ou relancez la surveillance pour explorer de nouvelles annonces.</p>
          </div>
        `;
        return;
      }}

      filtered.forEach(car => {{
        const card = document.createElement('div');
        card.className = car.is_sweet_spot ? 'car-card sweet-card' : 'car-card';

        const imgPlaceholder = 'https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=800&q=80';
        const imageSrc = car.img_url || imgPlaceholder;

        const badgeClass = car.budget_class === 'success' ? 'badge-success' :
                           car.budget_class === 'info' ? 'badge-info' :
                           car.budget_class === 'warning' ? 'badge-warning' : 'badge-danger';

        const mens5kClass = car.mens_5k <= 300 ? 'target-ok' : (car.mens_5k <= 325 ? 'target-warn' : '');
        const mens7kClass = car.mens_7k <= 300 ? 'target-ok' : (car.mens_7k <= 325 ? 'target-warn' : '');

        card.innerHTML = `
          <div class="card-image-wrap">
            <img class="card-image" src="${{imageSrc}}" alt="${{car.title}}" loading="lazy" onerror="this.src='${{imgPlaceholder}}'">
            <div class="image-overlay-badges">
              <span class="badge ${{badgeClass}}">${{car.budget_badge}}</span>
              <span class="badge score-badge">★ ${{car.score}}/10</span>
            </div>
          </div>
          <div class="card-body">
            <div class="car-header">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="car-model-name">${{car.model_name}}</span>
                ${{car.is_sweet_spot ? '<span class="chip" style="color:#22d3ee; border-color:rgba(6,182,212,0.4); font-weight:700">🎯 Cible Idéale</span>' : ''}}
              </div>
              <h2 class="car-title" title="${{car.title}}">${{car.title}}</h2>
            </div>

            <div class="price-tag">
              <span class="price-value">${{car.price_raw.toLocaleString('fr-FR')}} €</span>
              <span class="price-sub">Clé en main : ${{(car.price_raw + car.repat_cost).toLocaleString('fr-FR')}} €</span>
            </div>

            <div class="fin-box">
              <div class="fin-box-item">
                <span class="fin-box-label">Apport 5 000 €</span>
                <span class="fin-box-val ${{mens5kClass}}">${{car.mens_5k}} €<small style="font-size:0.75rem">/m</small></span>
              </div>
              <div class="fin-box-item">
                <span class="fin-box-label">Apport 7 000 €</span>
                <span class="fin-box-val ${{mens7kClass}}">${{car.mens_7k}} €<small style="font-size:0.75rem">/m</small></span>
              </div>
            </div>

            <div class="chips-grid">
              ${{car.km ? (car.km <= 60000 ? `<span class="chip" style="color:#34d399; font-weight:700; border-color:rgba(52,211,153,0.3)">🛣️ ${{car.km.toLocaleString('fr-FR')}} km (Idéal)</span>` : `<span class="chip">🛣️ ${{car.km.toLocaleString('fr-FR')}} km</span>`) : ''}}
              ${{car.year ? (car.year >= 2023 ? `<span class="chip" style="color:#67e8f9; font-weight:700; border-color:rgba(103,232,249,0.3)">📅 ${{car.year}} (Récent)</span>` : `<span class="chip">📅 ${{car.year}}</span>`) : ''}}
              ${{car.power_ch ? `<span class="chip">⚡ ${{car.power_ch}} ch (${{car.power_kw}} kW)</span>` : ''}}
              ${{car.trim_label ? `<span class="chip" style="color:#93c5fd; border-color:rgba(59,130,246,0.3)">🏷️ ${{car.trim_label}}</span>` : ''}}
              ${{car.price_drop > 0 ? `<span class="chip" style="color:#34d399; font-weight:700">📉 Baisse: -${{car.price_drop}} €</span>` : ''}}
            </div>

            <div class="card-footer">
              <div class="location-info">
                <span>📍 ${{car.city}} (${{car.zip}})</span>
              </div>
              <a href="${{car.ad_url}}" target="_blank" rel="noopener noreferrer" class="btn-view">
                Consulter ↗
              </a>
            </div>
          </div>
        `;

        container.appendChild(card);
      }});
    }}

    // Initialisation des graphiques Chart.js
    function initCharts() {{
      const ctxDeprec = document.getElementById('depreciationChart').getContext('2d');
      const ctxBudget = document.getElementById('budgetComparisonChart').getContext('2d');
      const stats = trendsData.stats_by_model || {{}};
      const budgetMax = trendsData.budget_ceiling_vehicle || 25631;

      const palette = [
        '#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6',
        '#06b6d4', '#14b8a6', '#f97316', '#6366f1'
      ];

      // 1. DATASETS COURBE DE DÉCOTE
      const labels = ['Aujourd\\'hui', '+3 mois', '+6 mois', '+9 mois', '+12 mois', '+18 mois', '+24 mois'];
      const datasets = [];
      let colorIdx = 0;

      // Ligne de budget horizontale
      datasets.push({{
        label: 'Plafond Budget BoursoBank (300€/m)',
        data: [budgetMax, budgetMax, budgetMax, budgetMax, budgetMax, budgetMax, budgetMax],
        borderColor: '#22c55e',
        borderWidth: 2,
        borderDash: [6, 6],
        pointRadius: 0,
        fill: false,
        order: 0
      }});

      for (const [mId, s] of Object.entries(stats)) {{
        const color = palette[colorIdx % palette.length];
        colorIdx++;
        datasets.push({{
          label: s.model_name.replace('Grande Autonomie', 'LR').replace('(Extended Range)', 'ER'),
          data: s.forecast_min_prices,
          borderColor: color,
          backgroundColor: color,
          borderWidth: 2,
          tension: 0.35,
          pointRadius: 3,
          pointHoverRadius: 6,
          fill: false,
          order: 1
        }});
      }}

      new Chart(ctxDeprec, {{
        type: 'line',
        data: {{ labels, datasets }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{ mode: 'index', intersect: false }},
          plugins: {{
            legend: {{
              position: 'bottom',
              labels: {{ color: '#9ca3af', font: {{ size: 10 }}, boxWidth: 12, padding: 10 }}
            }},
            tooltip: {{
              callbacks: {{
                label: function(context) {{
                  return context.dataset.label + ': ' + context.parsed.y.toLocaleString('fr-FR') + ' €';
                }}
              }}
            }}
          }},
          scales: {{
            x: {{
              grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
              ticks: {{ color: '#9ca3af', font: {{ size: 11 }} }}
            }},
            y: {{
              grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
              ticks: {{
                color: '#9ca3af',
                font: {{ size: 11 }},
                callback: function(val) {{ return (val / 1000) + ' k€'; }}
              }}
            }}
          }}
        }}
      }});

      // 2. BAR CHART COMPARATIF DES PRIX MIN ACTUELS
      const modelNames = [];
      const minPrices = [];
      const barColors = [];

      for (const [mId, s] of Object.entries(stats)) {{
        modelNames.push(s.model_name.split(' ')[0] + ' ' + (s.model_name.split(' ')[1] || ''));
        minPrices.push(s.min_price);
        barColors.push(s.min_price <= budgetMax ? '#10b981' : (s.min_price <= budgetMax + 2000 ? '#f59e0b' : '#3b82f6'));
      }}

      new Chart(ctxBudget, {{
        type: 'bar',
        data: {{
          labels: modelNames,
          datasets: [{{
            label: 'Prix Min Actuel (€)',
            data: minPrices,
            backgroundColor: barColors,
            borderRadius: 6
          }}]
        }},
        options: {{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: function(ctx) {{
                  const diff = ctx.parsed.x - budgetMax;
                  const diffStr = diff <= 0 ? ' (Dans le budget)' : ' (+' + diff.toLocaleString('fr-FR') + ' €)';
                  return ctx.parsed.x.toLocaleString('fr-FR') + ' €' + diffStr;
                }}
              }}
            }}
          }},
          scales: {{
            x: {{
              grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
              ticks: {{
                color: '#9ca3af',
                callback: function(val) {{ return (val / 1000) + ' k€'; }}
              }}
            }},
            y: {{
              grid: {{ display: false }},
              ticks: {{ color: '#e5e7eb', font: {{ size: 11 }} }}
            }}
          }}
        }}
      }});
    }}

    // Écouteurs sur les filtres
    document.querySelectorAll('.filter-btn').forEach(btn => {{
      btn.addEventListener('click', (e) => {{
        const btnElem = e.currentTarget;
        const type = btnElem.dataset.filterType;
        const val = btnElem.dataset.val;

        document.querySelectorAll(`.filter-btn[data-filter-type="${{type}}"]`).forEach(b => b.classList.remove('active'));
        btnElem.classList.add('active');

        if (type === 'budget') {{
          currentBudgetFilter = val;
        }} else if (type === 'model') {{
          currentModelFilter = val;
        }}

        renderListings();
      }});
    }});

    // Démarrage
    renderListings();
    initCharts();
  </script>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    res_path = os.path.join(BASE_DIR, "results.json")
    conf_path = os.path.join(BASE_DIR, "config.json")
    if os.path.exists(res_path) and os.path.exists(conf_path):
        with open(res_path, "r", encoding="utf-8") as f:
            res = json.load(f)
        with open(conf_path, "r", encoding="utf-8") as f:
            conf = json.load(f)
        out = build_html(res, conf)
        with open(os.path.join(BASE_DIR, "rapport_marche_ve.html"), "w", encoding="utf-8") as f:
            f.write(out)
        print("HTML dashboard generated successfully.")
