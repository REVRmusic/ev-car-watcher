#!/usr/bin/env python3
"""
Trends Engine - Analyse statistique, décote en temps réel et projection jusqu'en Mai 2027.
Échéance cible : 23 Mai 2027 (Restitution contrat LOA Peugeot e-2008 de Bastien).
Intégration du plan d'apport Mixify / Jean (11 625 € : 5 023 € résidences DJ + 6 602 € Mixify).
"""

import json
import math
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRENDS_PATH = os.path.join(BASE_DIR, "market_trends.json")

def calculate_monthly_payment(principal, annual_rate, duration_months):
    if principal <= 0:
        return 0.0
    r = annual_rate / 12.0
    if r == 0:
        return round(principal / duration_months, 2)
    m = principal * (r / (1.0 - (1.0 + r) ** (-duration_months)))
    return round(m, 2)

def compute_model_statistics_and_forecast(all_matched, config):
    financial = config.get("financial", {})
    annual_rate = financial.get("taux_taeg_annuel", 0.0435)
    duration = financial.get("duree_mois", 72)
    mens_max = financial.get("mensualite_max", 300.0)
    apport_7k = financial.get("apport_standard", 7000.0)
    apport_5k = financial.get("apport_base_dj", 5023.0)
    apport_mixify = financial.get("apport_mixify_cible", 11625.0)
    repat_cost = financial.get("cout_rapatriement_estime", 350.0)
    
    # Capacité d'emprunt max BoursoBank (mensualité 300 € sur 72 mois à 4,35 %)
    r = annual_rate / 12.0
    loan_max = mens_max * (1.0 - (1.0 + r)**(-duration)) / r
    budget_max_standard = loan_max + apport_7k - repat_cost # Plafond standard (~25 631 €)
    budget_max_mixify = loan_max + apport_mixify - repat_cost # Plafond Mixify (~30 256 €)

    # Taux annuel de décote estimé pour les VE d'occasion récents (12%/an)
    annual_depreciation = 0.12

    # L'horizon s'arrête exactement en Mai 2027 (Mois 0 à Mois 6)
    # Novembre 2026 -> Mai 2027 = 6 mois
    forecast_timeline = [0, 1, 2, 3, 4, 5, 6]
    forecast_labels = [
        "Nov 2026 (Actuel)",
        "Déc 2026",
        "Jan 2027",
        "Fév 2027",
        "Mar 2027",
        "Avr 2027",
        "Mai 2027 (Échéance LOA)"
    ]

    stats_by_model = {}
    
    for model_conf in config.get("models", []):
        m_id = model_conf["id"]
        m_name = model_conf["name"]
        
        m_listings = [x for x in all_matched if x["model_id"] == m_id]
        
        if not m_listings:
            continue
            
        prices = sorted([x["price_raw"] for x in m_listings])
        kms = sorted([x["km"] for x in m_listings if x.get("km")])
        
        min_p = prices[0]
        max_p = prices[-1]
        avg_p = int(sum(prices) / len(prices))
        median_p = prices[len(prices) // 2]
        avg_km = int(sum(kms) / len(kms)) if kms else 0
        
        in_budget_items = [x for x in m_listings if x["budget_status"] in ["EXCELLENT_DEAL", "WITHIN_BUDGET"]]
        
        # Courbe prévisionnelle mensuelle jusqu'en Mai 2027 (7 points)
        forecast_min_prices = [round(min_p * ((1.0 - annual_depreciation) ** (m / 12.0))) for m in forecast_timeline]
        forecast_median_prices = [round(median_p * ((1.0 - annual_depreciation) ** (m / 12.0))) for m in forecast_timeline]

        # Prix et mensualités projetés en Mai 2027
        price_mai_2027 = forecast_min_prices[-1]
        loan_mai_7k = max(0, price_mai_2027 + repat_cost - apport_7k)
        loan_mai_5k = max(0, price_mai_2027 + repat_cost - apport_5k)
        loan_mai_mixify = max(0, price_mai_2027 + repat_cost - apport_mixify)
        
        mens_mai_2027_7k = calculate_monthly_payment(loan_mai_7k, annual_rate, duration)
        mens_mai_2027_5k = calculate_monthly_payment(loan_mai_5k, annual_rate, duration)
        mens_mai_2027_mixify = calculate_monthly_payment(loan_mai_mixify, annual_rate, duration)

        # Mensualités actuelles
        loan_cur_mixify = max(0, min_p + repat_cost - apport_mixify)
        min_mens_mixify = calculate_monthly_payment(loan_cur_mixify, annual_rate, duration)

        # Délai d'accessibilité au budget standard (7k€)
        if min_p <= budget_max_standard:
            months_to_budget = 0
            budget_horizon = "Immédiat (Déjà dans le budget)"
            horizon_class = "success"
        else:
            months_to_budget = math.ceil(math.log(budget_max_standard / min_p) / math.log(1 - annual_depreciation) * 12)
            if months_to_budget <= 6:
                budget_horizon = f"Accessible d'ici Mai 2027 (~{months_to_budget} mois)"
                horizon_class = "warning"
            else:
                budget_horizon = f"D'ici ~{months_to_budget} mois"
                horizon_class = "secondary"

        # Statut spécifique Mai 2027 avec apport Mixify (11 625 €)
        if m_id == "peugeot_e3008_gt":
            if mens_mai_2027_mixify <= mens_max:
                status_mai_2027 = "👑 Cible Mixify Validée (≤ 300€/m) !"
                status_mai_class = "emerald"
            else:
                status_mai_2027 = "⚡ Objectif Mixify en cours"
                status_mai_class = "warning"
        elif min_p <= budget_max_standard:
            status_mai_2027 = "🔥 Déjà dans le budget (apport 7k€)"
            status_mai_class = "success"
        elif mens_mai_2027_mixify <= mens_max:
            status_mai_2027 = "🎯 Dans le budget Mixify (11.6k€)"
            status_mai_class = "emerald"
        elif mens_mai_2027_7k <= mens_max:
            status_mai_2027 = "🎯 Dans le budget standard en Mai"
            status_mai_class = "info"
        else:
            status_mai_2027 = "⏳ Décote en cours"
            status_mai_class = "secondary"

        stats_by_model[m_id] = {
            "model_id": m_id,
            "model_name": m_name,
            "count": len(m_listings),
            "in_budget_count": len(in_budget_items),
            "min_price": min_p,
            "max_price": max_p,
            "avg_price": avg_p,
            "median_price": median_p,
            "avg_km": avg_km,
            "min_mens_7k": min([x["mens_7k"] for x in m_listings]),
            "min_mens_5k": min([x["mens_5k"] for x in m_listings]),
            "min_mens_mixify": min_mens_mixify,
            "months_to_budget": months_to_budget,
            "budget_horizon": budget_horizon,
            "horizon_class": horizon_class,
            "forecast_timeline": forecast_timeline,
            "forecast_labels": forecast_labels,
            "forecast_min_prices": forecast_min_prices,
            "forecast_median_prices": forecast_median_prices,
            "price_mai_2027": price_mai_2027,
            "mens_mai_2027_7k": mens_mai_2027_7k,
            "mens_mai_2027_5k": mens_mai_2027_5k,
            "mens_mai_2027_mixify": mens_mai_2027_mixify,
            "status_mai_2027": status_mai_2027,
            "status_mai_class": status_mai_class,
        }

    # Mise à jour de l'historique persistant market_trends.json
    history_data = {"snapshots": []}
    if os.path.exists(TRENDS_PATH):
        try:
            with open(TRENDS_PATH, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        except Exception:
            history_data = {"snapshots": []}

    now = datetime.now()
    now_date = now.strftime("%Y-%m-%d")
    now_iso = now.isoformat()

    snapshot = {
        "timestamp": now_iso,
        "date": now_date,
        "budget_ceiling_standard": round(budget_max_standard, 2),
        "budget_ceiling_mixify": round(budget_max_mixify, 2),
        "models": {
            m_id: {
                "min": data["min_price"],
                "avg": data["avg_price"],
                "median": data["median_price"],
                "count": data["count"],
                "in_budget": data["in_budget_count"],
                "price_mai_2027": data["price_mai_2027"],
                "mens_mai_2027_7k": data["mens_mai_2027_7k"],
                "mens_mai_2027_mixify": data["mens_mai_2027_mixify"]
            }
            for m_id, data in stats_by_model.items()
        }
    }

    snapshots = history_data.get("snapshots", [])
    if snapshots and snapshots[-1].get("date") == now_date:
        snapshots[-1] = snapshot
    else:
        snapshots.append(snapshot)
    history_data["snapshots"] = snapshots

    with open(TRENDS_PATH, "w", encoding="utf-8") as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)

    return {
        "stats_by_model": stats_by_model,
        "budget_ceiling_standard": round(budget_max_standard, 2),
        "budget_ceiling_mixify": round(budget_max_mixify, 2),
        "forecast_labels": forecast_labels,
        "snapshots_history": snapshots
    }
