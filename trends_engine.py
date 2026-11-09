import json
import math
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRENDS_PATH = os.path.join(BASE_DIR, "market_trends.json")

def compute_model_statistics_and_forecast(all_matched, config):
    financial = config.get("financial", {})
    annual_rate = financial.get("taux_taeg_annuel", 0.0435)
    duration = financial.get("duree_mois", 72)
    mens_max = financial.get("mensualite_max", 300.0)
    apport_7k = financial.get("apport_max", 7000.0)
    repat_cost = financial.get("cout_rapatriement_estime", 350.0)
    
    # Capacité d'emprunt max BoursoBank
    r = annual_rate / 12.0
    loan_max = mens_max * (1.0 - (1.0 + r)**(-duration)) / r
    budget_max_vehicle = loan_max + apport_7k - repat_cost # Prix max du véhicule clé en main

    # Taux annuel de décote estimé pour les VE d'occasion récents (12%/an)
    annual_depreciation = 0.12
    monthly_deprec_factor = (1.0 - annual_depreciation) ** (1.0 / 12.0)

    stats_by_model = {}
    
    for model_conf in config.get("models", []):
        m_id = model_conf["id"]
        m_name = model_conf["name"]
        
        # Listings pour ce modèle
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
        
        # Délai estimé d'accessibilité au budget (mois)
        if min_p <= budget_max_vehicle:
            months_to_budget = 0
            budget_horizon = "Immédiat (Déjà dans le budget)"
            horizon_class = "success"
        else:
            months_to_budget = math.ceil(math.log(budget_max_vehicle / min_p) / math.log(1 - annual_depreciation) * 12)
            if months_to_budget <= 6:
                budget_horizon = f"D'ici ~{months_to_budget} mois (Court terme)"
                horizon_class = "warning"
            elif months_to_budget <= 12:
                budget_horizon = f"D'ici ~{months_to_budget} mois (Moyen terme)"
                horizon_class = "info"
            else:
                budget_horizon = f"D'ici ~{months_to_budget} mois"
                horizon_class = "secondary"

        # Courbe prévisionnelle sur 24 mois pour ce modèle
        # Points à : M0 (Aujourd'hui), M+3, M+6, M+9, M+12, M+18, M+24
        forecast_timeline = [0, 3, 6, 9, 12, 18, 24]
        forecast_min_prices = [round(min_p * ((1.0 - annual_depreciation) ** (m / 12.0))) for m in forecast_timeline]
        forecast_median_prices = [round(median_p * ((1.0 - annual_depreciation) ** (m / 12.0))) for m in forecast_timeline]

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
            "months_to_budget": months_to_budget,
            "budget_horizon": budget_horizon,
            "horizon_class": horizon_class,
            "forecast_timeline": forecast_timeline,
            "forecast_min_prices": forecast_min_prices,
            "forecast_median_prices": forecast_median_prices,
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

    # Création du snapshot
    snapshot = {
        "timestamp": now_iso,
        "date": now_date,
        "models": {
            m_id: {
                "min": data["min_price"],
                "avg": data["avg_price"],
                "median": data["median_price"],
                "count": data["count"],
                "in_budget": data["in_budget_count"]
            }
            for m_id, data in stats_by_model.items()
        }
    }

    # Si déjà un snapshot pour aujourd'hui, on le met à jour
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
        "budget_ceiling_vehicle": round(budget_max_vehicle, 2),
        "snapshots_history": snapshots
    }
