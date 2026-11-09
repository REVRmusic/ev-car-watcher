#!/usr/bin/env python3
"""
Générateur de tableau de bord HTML haut de gamme pour la veille des véhicules électriques.
Design moderne, épuré, responsive, avec observatoire des décotes et courbes prévisionnelles arrêtées en Mai 2027.
Échéance cible : 23 Mai 2027 (Restitution LOA Peugeot e-2008 de Bastien / LM MUSIC).
"""

import json
from datetime import datetime

def build_html(results_data, config):
    listings = results_data.get("listings", [])
    financial = config.get("financial", {})
    criteria = config.get("criteria", {})
    trends = results_data.get("trends", {})
    stats_by_model = trends.get("stats_by_model", {})
    budget_ceiling = trends.get("budget_ceiling_vehicle", 23600.0)
    models_config = {m["id"]: m for m in config.get("models", [])}
    
    generated_at = datetime.fromisoformat(results_data.get("generated_at", datetime.now().isoformat())).strftime("%d/%m/%Y à %H:%M")
    
    total_listings = len(listings)
    in_budget_count = results_data.get("in_budget_count", 0)
    negotiable_count = results_data.get("negotiable_count", 0)
    new_count = results_data.get("new_count", 0)
    price_drop_count = results_data.get("price_drop_count", 0)
    sweet_spot_count = len([x for x in listings if x.get("is_sweet_spot") and x.get("budget_status") in ["EXCELLENT_DEAL", "WITHIN_BUDGET"]])
    autohero_count = len([x for x in listings if x.get("source") == "Autohero"])

    # Données JSON pour les scripts clients (annonces et statistiques prévisionnelles)
    listings_json = json.dumps(listings, ensure_ascii=False)
    trends_json = json.dumps(trends, ensure_ascii=False)
    models_json = json.dumps(config.get("models", []), ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="fr" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Observatoire & Veille Véhicules Électriques — Cap Mai 2027</title>
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
      --accent-orange: #f97316;
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
      max-width: 1440px;
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

    /* SOURCES CHIPS */
    .sources-chips {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      flex-wrap: wrap;
    }}

    .source-chip {{
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      border: 1px solid transparent;
    }}

    .source-chip.active {{
      background-color: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border-color: rgba(16, 185, 129, 0.4);
    }}

    .source-chip.portal {{
      background-color: rgba(59, 130, 246, 0.15);
      color: #93c5fd;
      border-color: rgba(59, 130, 246, 0.3);
      text-decoration: none;
      transition: all 0.2s ease;
    }}

    .source-chip.portal:hover {{
      background-color: rgba(59, 130, 246, 0.3);
      transform: translateY(-1px);
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
    .kpi-card.purple::before {{ background: linear-gradient(90deg, var(--accent-purple), transparent); }}

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
      padding: 0.25rem 0.6rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 700;
    }}

    .tag-horizon.success {{
      background-color: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}

    .tag-horizon.emerald {{
      background-color: rgba(16, 185, 129, 0.2);
      color: #10b981;
      border: 1px solid #10b981;
    }}

    .tag-horizon.warning {{
      background-color: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }}

    .tag-horizon.info {{
      background-color: rgba(59, 130, 246, 0.15);
      color: #93c5fd;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }}

    .tag-horizon.secondary {{
      background-color: rgba(107, 114, 128, 0.15);
      color: #9ca3af;
      border: 1px solid rgba(107, 114, 128, 0.3);
    }}

    /* CHARTS CONTAINER */
    .charts-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
      gap: 1.5rem;
      margin-top: 0.5rem;
    }}

    @media (max-width: 768px) {{
      .charts-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .chart-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 0.85rem;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .chart-title {{
      font-size: 0.95rem;
      font-weight: 700;
      color: #ffffff;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .chart-legend-hint {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 400;
    }}

    .chart-canvas-wrap {{
      position: relative;
      height: 320px;
      width: 100%;
    }}

    /* CONTROLS / FILTERS */
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

    .filters-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.75rem;
    }}

    .filter-btn {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      padding: 0.45rem 0.9rem;
      border-radius: 0.5rem;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .filter-btn:hover {{
      background-color: var(--bg-card-hover);
      color: var(--text-primary);
      border-color: rgba(59, 130, 246, 0.4);
    }}

    .filter-btn.active {{
      background-color: var(--accent-blue);
      border-color: var(--accent-blue);
      color: #ffffff;
      box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);
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
      color: #fbbf24;
      border: 1px solid rgba(251, 191, 36, 0.5);
    }}

    .source-tag {{
      position: absolute;
      bottom: 0.75rem;
      left: 0.75rem;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      padding: 0.25rem 0.55rem;
      border-radius: 0.35rem;
      font-size: 0.7rem;
      font-weight: 700;
      backdrop-filter: blur(8px);
    }}

    .source-tag.autoscout {{
      background-color: rgba(30, 58, 138, 0.85);
      color: #93c5fd;
      border: 1px solid #3b82f6;
    }}

    .source-tag.autohero {{
      background-color: rgba(194, 65, 12, 0.85);
      color: #fed7aa;
      border: 1px solid #f97316;
    }}

    .card-body {{
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
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
      color: var(--accent-blue);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .car-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.35;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .price-tag {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.75rem;
    }}

    .price-value {{
      font-size: 1.5rem;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      color: #ffffff;
    }}

    .price-sub {{
      font-size: 0.8rem;
      color: var(--text-muted);
    }}

    /* FINANCING SIMULATION BOX */
    .fin-box {{
      background: linear-gradient(145deg, rgba(15, 23, 42, 0.7), rgba(30, 41, 59, 0.5));
      border: 1px solid rgba(59, 130, 246, 0.2);
      border-radius: 0.75rem;
      padding: 0.85rem;
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
      text-transform: uppercase;
      font-weight: 600;
      color: var(--text-muted);
    }}

    .fin-box-val {{
      font-size: 1.15rem;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      color: #60a5fa;
    }}

    .fin-box-val.target-ok {{
      color: #34d399;
    }}

    .fin-box-val.target-warn {{
      color: #fbbf24;
    }}

    /* CHIPS GRID */
    .chips-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
    }}

    .chip {{
      font-size: 0.75rem;
      background-color: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 0.25rem 0.55rem;
      border-radius: 0.4rem;
      color: var(--text-secondary);
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }}

    .card-footer {{
      margin-top: auto;
      padding-top: 0.75rem;
      border-top: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .location-info {{
      font-size: 0.75rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .btn-view {{
      background-color: var(--accent-blue-soft);
      border: 1px solid var(--accent-blue);
      color: #93c5fd;
      padding: 0.4rem 0.85rem;
      border-radius: 0.5rem;
      font-size: 0.8rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .btn-view:hover {{
      background-color: var(--accent-blue);
      color: #ffffff;
      box-shadow: 0 0 10px rgba(59, 130, 246, 0.4);
    }}

    .empty-state {{
      grid-column: 1 / -1;
      padding: 4rem 2rem;
      text-align: center;
      background-color: var(--bg-card);
      border: 1px dashed var(--border-color);
      border-radius: 1rem;
      color: var(--text-muted);
    }}
  </style>
</head>
<body>
  <div class="container">
    <!-- HEADER -->
    <header>
      <div class="header-top">
        <div class="title-group">
          <h1>⚡ EV Car Watcher — Cap Mai 2027</h1>
          <p>Surveillance du marché des véhicules électriques d'occasion & Projection de décote BoursoBank pour Bastien (LM MUSIC)</p>
        </div>
        <div class="meta-badge">
          <span class="dot"></span>
          <span>Actualisé le {generated_at}</span>
        </div>
      </div>

      <!-- BANDEAU SIMULATION FINANCIÈRE BOURSOBANK -->
      <div class="financial-banner">
        <div class="financial-details">
          <div class="fin-item">
            <span>Banque & Offre</span>
            <span>{financial.get('banque', 'BoursoBank')} (Prêt Véhicule Propre)</span>
          </div>
          <div class="fin-item">
            <span>Taux Fixe TAEG</span>
            <span>{financial.get('taux_taeg_annuel', 0.0435)*100:.2f} % (Avec Justificatif)</span>
          </div>
          <div class="fin-item">
            <span>Durée Amortissable</span>
            <span>{financial.get('duree_mois', 72)} mois (6 ans)</span>
          </div>
          <div class="fin-item">
            <span>Mensualité Cible</span>
            <span style="color:#34d399">≤ {financial.get('mensualite_max', 300):.0f} € / mois</span>
          </div>
          <div class="fin-item">
            <span>Apport Prévu</span>
            <span>5 000 € à 7 000 €</span>
          </div>
          <div class="fin-item">
            <span>Date Butoir Projet</span>
            <span style="color:#f59e0b">23 Mai 2027 (Restitution LOA 2008)</span>
          </div>
        </div>

        <div class="sources-chips">
          <span class="source-chip active">● AutoScout24</span>
          <span class="source-chip active">● Autohero Reconditionné</span>
          <a href="https://www.spoticar.fr/voitures-occasion/peugeot/3008" target="_blank" rel="noopener noreferrer" class="source-chip portal">↗ Spoticar e-3008</a>
          <a href="https://www.lacentrale.fr/listing?energies=elec" target="_blank" rel="noopener noreferrer" class="source-chip portal">↗ La Centrale</a>
        </div>
      </div>
    </header>

    <!-- KPI STATS CARDS -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <span class="kpi-label">Annonces Surveillées</span>
        <span class="kpi-value">{total_listings}</span>
        <span class="kpi-subtext">Multi-sources ({total_listings - autohero_count} AutoScout24 + {autohero_count} Autohero)</span>
      </div>
      <div class="kpi-card emerald">
        <span class="kpi-label">Dans le Budget Actuel</span>
        <span class="kpi-value">{in_budget_count}</span>
        <span class="kpi-subtext">≤ 300 €/mois (BoursoBank 4,35 % sur 72m)</span>
      </div>
      <div class="kpi-card cyan">
        <span class="kpi-label">Cible Idéale (Sweet Spot)</span>
        <span class="kpi-value">{sweet_spot_count}</span>
        <span class="kpi-subtext">2023–2025 & ≤ 60 000 km & dans le budget</span>
      </div>
      <div class="kpi-card amber">
        <span class="kpi-label">Négociables Immédiates</span>
        <span class="kpi-value">{negotiable_count}</span>
        <span class="kpi-subtext">Dépassement &lt; 25 €/mois (&lt; 1 600 € d'effort)</span>
      </div>
      <div class="kpi-card purple">
        <span class="kpi-label">Horizon Échéance LOA</span>
        <span class="kpi-value" style="color:#c084fc">Mai 2027</span>
        <span class="kpi-subtext">Fin contrat Peugeot e-2008 (reste 6 mois)</span>
      </div>
    </div>

    <!-- OBSERVATOIRE DES PRIX & COURBES DE DÉCOTE -->
    <section class="observatory-section">
      <div class="section-header">
        <div>
          <h2 class="section-title">📊 Observatoire de Marché & Trajectoire vers Mai 2027</h2>
          <p class="section-subtitle">Suivi des prix réels constatés et projections mathématiques jusqu'à l'échéance de votre LOA le 23 mai 2027 (Plafond clé en main : {budget_ceiling:,.0f} €)</p>
        </div>
      </div>

      <!-- TABLEAU DES FOURCHETTES PAR MODÈLE -->
      <div class="table-container">
        <table class="trends-table">
          <thead>
            <tr>
              <th>Modèle & Atouts Clés (DJ / Logistique)</th>
              <th>Annonces</th>
              <th>Prix Min Actuel</th>
              <th>Prix Médian</th>
              <th>Prix Estimé Mai 2027</th>
              <th>Mensualité Mai 2027 (Apport 7k€)</th>
              <th>Statut Mai 2027</th>
              <th>Accès Plateformes</th>
            </tr>
          </thead>
          <tbody>
"""

    for m_id, stats in stats_by_model.items():
        m_conf = models_config.get(m_id, {})
        min_p = f"{stats['min_price']:,} €".replace(",", " ")
        med_p = f"{stats['median_price']:,} €".replace(",", " ")
        p_mai = f"{stats.get('price_mai_2027', 0):,} €".replace(",", " ")
        mens_mai = f"{stats.get('mens_mai_2027_7k', 0)} €/m"
        st_mai = stats.get('status_mai_2027', 'En cours')
        st_class = stats.get('status_mai_class', 'info')
        
        # Badges d'atouts spécifiques Bastien / DJ
        features = []
        if m_conf.get("trunk_liters"):
            features.append(f"📦 {m_conf['trunk_liters']} L")
        if m_conf.get("has_v2l"):
            features.append(f"⚡ V2L {m_conf.get('v2l_power', '3 kW')}")
        if m_conf.get("has_kw_display"):
            features.append("📊 kW direct")
        if m_conf.get("has_pac"):
            features.append("❄️ PAC")
        feat_str = " · ".join(features)

        spot_url = m_conf.get("spoticar_url", "https://www.spoticar.fr")
        lc_url = m_conf.get("lacentrale_url", "https://www.lacentrale.fr")
        as_url = m_conf.get("url", "#")

        html += f"""
            <tr>
              <td>
                <div class="cell-model">{stats['model_name']}</div>
                <div style="font-size:0.75rem; color:#9ca3af; margin-top:2px;">{feat_str}</div>
              </td>
              <td class="cell-mono">{stats['count']}</td>
              <td class="cell-mono" style="color:#34d399; font-weight:700;">{min_p}</td>
              <td class="cell-mono">{med_p}</td>
              <td class="cell-mono" style="color:#60a5fa; font-weight:700;">{p_mai}</td>
              <td class="cell-mono" style="font-weight:700; color:{'#34d399' if stats.get('mens_mai_2027_7k', 999) <= 300 else '#fbbf24'};">{mens_mai}</td>
              <td><span class="tag-horizon {st_class}">{st_mai}</span></td>
              <td>
                <div style="display:flex; gap:0.35rem;">
                  <a href="{as_url}" target="_blank" rel="noopener noreferrer" style="font-size:0.7rem; color:#93c5fd; text-decoration:none; padding:2px 6px; background:rgba(59,130,246,0.15); border-radius:4px; border:1px solid rgba(59,130,246,0.3)">AutoScout</a>
                  <a href="{spot_url}" target="_blank" rel="noopener noreferrer" style="font-size:0.7rem; color:#fca5a5; text-decoration:none; padding:2px 6px; background:rgba(239,68,68,0.15); border-radius:4px; border:1px solid rgba(239,68,68,0.3)">Spoticar</a>
                  <a href="{lc_url}" target="_blank" rel="noopener noreferrer" style="font-size:0.7rem; color:#fde047; text-decoration:none; padding:2px 6px; background:rgba(234,179,8,0.15); border-radius:4px; border:1px solid rgba(234,179,8,0.3)">LaCentrale</a>
                </div>
              </td>
            </tr>
        """

    html += f"""
          </tbody>
        </table>
      </div>

      <!-- GRAPHIQUES INTERACTIFS -->
      <div class="charts-grid">
        <!-- COURBE PRÉVISIONNELLE ARRÊTÉE EN MAI 2027 -->
        <div class="chart-card">
          <div class="chart-title">
            <span>📈 Courbes Prévisionnelles de Décote (Cap Mai 2027)</span>
            <span class="chart-legend-hint">Échéance : 23 Mai 2027 (Restitution LOA e-2008)</span>
          </div>
          <div class="chart-canvas-wrap">
            <canvas id="depreciationChart"></canvas>
          </div>
        </div>

        <!-- POSITIONNEMENT ACTUEL PAR MODÈLE -->
        <div class="chart-card">
          <div class="chart-title">
            <span>⚖️ Prix Minimum Actuel vs Plafond Budget Clé en Main</span>
          </div>
          <div class="chart-canvas-wrap">
            <canvas id="budgetComparisonChart"></canvas>
          </div>
        </div>
      </div>
    </section>

    <!-- FILTRES INTERACTIFS -->
    <div class="controls-panel">
      <div class="filters-row">
        <span style="font-size:0.8rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-right:0.5rem;">Statut :</span>
        <button class="filter-btn active" data-filter="all">Toutes ({total_listings})</button>
        <button class="filter-btn sweet-btn" data-filter="sweet_spot">🎯 Cibles Idéales (2023+ &amp; ≤60k km &amp; Budget) ({sweet_spot_count})</button>
        <button class="filter-btn" data-filter="budget_ok">✅ Dans le budget ({in_budget_count})</button>
        <button class="filter-btn" data-filter="negotiable">⚡ Négociables ({negotiable_count})</button>
        <button class="filter-btn" data-filter="pepite">💎 Pépites (Score ≥ 8/10)</button>
        <button class="filter-btn" data-filter="autohero">🛡️ Autohero Reconditionné ({autohero_count})</button>
      </div>

      <div class="filters-row" style="margin-top:0.25rem;">
        <span style="font-size:0.8rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-right:0.5rem;">Modèle :</span>
        <button class="filter-btn model-btn active" data-model="all">Tous les modèles</button>
        <button class="filter-btn model-btn" data-model="skoda_enyaq_80">Skoda Enyaq 80</button>
        <button class="filter-btn model-btn" data-model="mustang_mache_er">Mustang Mach-E</button>
        <button class="filter-btn model-btn" data-model="megane_etech_iconic">Mégane E-Tech</button>
        <button class="filter-btn model-btn" data-model="hyundai_ioniq_5">Ioniq 5</button>
        <button class="filter-btn model-btn" data-model="kia_ev6">Kia EV6</button>
        <button class="filter-btn model-btn" data-model="kia_niro_ev_premium">Kia Niro EV</button>
        <button class="filter-btn model-btn" data-model="byd_seal_u_design">BYD Seal U</button>
        <button class="filter-btn model-btn" data-model="hyundai_kona_2_exec">Kona 2 Exec</button>
        <button class="filter-btn model-btn" data-model="peugeot_e3008_gt">Peugeot e-3008 GT</button>
      </div>
    </div>

    <!-- GRILLE DES OFFRES QUALIFIÉES -->
    <main class="cars-grid" id="cars-grid">
      <!-- Rempli dynamiquement par JS -->
    </main>
  </div>

  <script>
    const listingsData = {listings_json};
    const trendsData = {trends_json};
    const modelsData = {models_json};
    let currentBudgetFilter = 'all';
    let currentModelFilter = 'all';

    function renderListings() {{
      const container = document.getElementById('cars-grid');
      container.innerHTML = '';

      const filtered = listingsData.filter(item => {{
        if (currentModelFilter !== 'all' && item.model_id !== currentModelFilter) {{
          return false;
        }}
        if (currentBudgetFilter === 'sweet_spot') {{
          return item.is_sweet_spot && (item.budget_status === 'EXCELLENT_DEAL' || item.budget_status === 'WITHIN_BUDGET');
        }} else if (currentBudgetFilter === 'budget_ok') {{
          return item.budget_status === 'EXCELLENT_DEAL' || item.budget_status === 'WITHIN_BUDGET';
        }} else if (currentBudgetFilter === 'negotiable') {{
          return item.budget_status === 'NEGOTIABLE';
        }} else if (currentBudgetFilter === 'pepite') {{
          return item.score >= 8.0;
        }} else if (currentBudgetFilter === 'autohero') {{
          return item.source === 'Autohero';
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

        const isAutohero = car.source === 'Autohero';
        const sourceTagHtml = isAutohero 
          ? `<span class="source-tag autohero">🛡️ Autohero Reconditionné</span>`
          : `<span class="source-tag autoscout">🌐 AutoScout24</span>`;

        card.innerHTML = `
          <div class="card-image-wrap">
            <img class="card-image" src="${{imageSrc}}" alt="${{car.title}}" loading="lazy" onerror="this.src='${{imgPlaceholder}}'">
            <div class="image-overlay-badges">
              <span class="badge ${{badgeClass}}">${{car.budget_badge}}</span>
              <span class="badge score-badge">★ ${{car.score}}/10</span>
            </div>
            ${{sourceTagHtml}}
          </div>
          <div class="card-body">
            <div class="car-header">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="car-model-name">${{car.model_name}}</span>
                ${{car.is_sweet_spot ? '<span class="chip" style="color:#22d3ee; border-color:rgba(6,182,212,0.4); font-weight:700">🎯 Cible Idéale</span>' : ''}}
              </div>
              <h2 class="car-title" title="${{car.version_input ? car.version_input : car.title}}">${{car.version_input ? car.version_input : car.title}}</h2>
            </div>

            <div class="price-tag">
              <span class="price-value">${{car.price_raw.toLocaleString('fr-FR')}} €</span>
              <span class="price-sub">Clé en main : ${{(car.price_raw + (car.repat_cost || 350)).toLocaleString('fr-FR')}} €</span>
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
              ${{car.has_v2l ? `<span class="chip" style="color:#f59e0b; border-color:rgba(245,158,11,0.4)">⚡ Prise V2L 230V (${{car.v2l_power || '3 kW'}})</span>` : ''}}
              ${{car.trunk_liters ? `<span class="chip">📦 Coffre ${{car.trunk_liters}} L</span>` : ''}}
              ${{car.has_kw_display ? `<span class="chip">📊 kW direct</span>` : ''}}
              ${{car.has_pac ? `<span class="chip" style="color:#a7f3d0">❄️ Pompe à Chaleur</span>` : ''}}
              ${{car.has_warranty ? `<span class="chip" style="color:#fdba74">🛡️ ${{car.warranty_text || 'Garantie incluse'}}</span>` : ''}}
              ${{car.trim_label && car.trim_label !== 'À vérifier' ? `<span class="chip" style="color:#93c5fd; border-color:rgba(59,130,246,0.3)">🏷️ ${{car.trim_label}}</span>` : ''}}
              ${{car.price_drop > 0 ? `<span class="chip" style="color:#34d399; font-weight:700">📉 Baisse: -${{car.price_drop}} €</span>` : ''}}
            </div>

            <div class="card-footer">
              <div class="location-info">
                <span>📍 ${{car.city}}${{car.zip ? ' (' + car.zip + ')' : ''}}</span>
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
      const budgetMax = trendsData.budget_ceiling_vehicle || 23600;

      const palette = [
        '#38bdf8', '#34d399', '#a78bfa', '#f472b6', '#fbbf24',
        '#4ade80', '#2dd4bf', '#fb923c', '#818cf8', '#e879f9'
      ];

      // 1. DATASETS COURBE DE DÉCOTE ARRÊTÉE EN MAI 2027
      const labels = trendsData.forecast_labels || [
        'Nov 2026 (Actuel)', 'Déc 2026', 'Jan 2027', 'Fév 2027', 'Mar 2027', 'Avr 2027', 'Mai 2027 (Échéance LOA)'
      ];
      const datasets = [];
      let colorIdx = 0;

      // Ligne de budget BoursoBank horizontale (300 € / mois)
      datasets.push({{
        label: 'Plafond Budget BoursoBank (300€/m sur 72m)',
        data: Array(labels.length).fill(budgetMax),
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
          tension: 0.3,
          pointRadius: [3, 3, 3, 3, 3, 3, 6], // Point plus large sur Mai 2027
          pointHoverRadius: 7,
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
              ticks: {{ color: '#9ca3af', font: {{ size: 10 }} }}
            }},
            y: {{
              grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
              ticks: {{
                color: '#9ca3af',
                font: {{ size: 11 }},
                callback: function(val) {{ return (val / 1000).toFixed(0) + ' k€'; }}
              }}
            }}
          }}
        }}
      }});

      // 2. POSITIONNEMENT ACTUEL VS PLAFOND
      const barLabels = [];
      const barPrices = [];
      const barColors = [];

      for (const [mId, s] of Object.entries(stats)) {{
        barLabels.push(s.model_name.split(' (')[0].replace('Grande Autonomie', 'LR'));
        barPrices.push(s.min_price);
        barColors.push(s.min_price <= budgetMax ? '#10b981' : (s.min_price <= budgetMax + 1600 ? '#f59e0b' : '#ef4444'));
      }}

      new Chart(ctxBudget, {{
        type: 'bar',
        data: {{
          labels: barLabels,
          datasets: [{{
            label: 'Prix Minimum Constaté (€)',
            data: barPrices,
            backgroundColor: barColors,
            borderRadius: 6,
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: function(ctx) {{
                  return 'Prix Min : ' + ctx.parsed.x.toLocaleString('fr-FR') + ' € (Plafond : ' + Math.round(budgetMax).toLocaleString('fr-FR') + ' €)';
                }}
              }}
            }}
          }},
          scales: {{
            x: {{
              grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
              ticks: {{
                color: '#9ca3af',
                callback: function(val) {{ return (val / 1000).toFixed(0) + ' k€'; }}
              }}
            }},
            y: {{
              grid: {{ display: false }},
              ticks: {{ color: '#f3f4f6', font: {{ size: 11 }} }}
            }}
          }}
        }}
      }});
    }}

    // Gestion des écouteurs de filtres
    document.querySelectorAll('.filter-btn:not(.model-btn)').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.filter-btn:not(.model-btn)').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentBudgetFilter = btn.dataset.filter;
        renderListings();
      }});
    }});

    document.querySelectorAll('.model-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.model-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentModelFilter = btn.dataset.model;
        renderListings();
      }});
    }});

    // Initialisation au chargement
    document.addEventListener('DOMContentLoaded', () => {{
      renderListings();
      initCharts();
    }});
  </script>
</body>
</html>"""
    return html
