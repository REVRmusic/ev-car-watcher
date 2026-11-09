#!/usr/bin/env python3
"""
EV Market Watcher - Surveillance intelligente multi-sources du marché des véhicules électriques d'occasion
Sources : AutoScout24 & Autohero (avec liens pré-configurés Spoticar & La Centrale)
Objectif : Remplacement LOA Peugeot e-2008 à échéance Mai 2027 (Budget max 300 €/m BoursoBank)
"""

import json
import os
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from generate_dashboard import build_html
from trends_engine import compute_model_statistics_and_forecast
from autohero_fetcher import fetch_autohero_listings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
HISTORY_PATH = os.path.join(BASE_DIR, "history.json")
RESULTS_PATH = os.path.join(BASE_DIR, "results.json")
REPORT_HTML_PATH = os.path.join(BASE_DIR, "rapport_marche_ve.html")
INDEX_HTML_PATH = os.path.join(BASE_DIR, "index.html")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_history(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def calculate_monthly_payment(principal, annual_rate, duration_months):
    """Calcule la mensualité d'un prêt amortissable."""
    if principal <= 0:
        return 0.0
    r = annual_rate / 12.0
    if r == 0:
        return round(principal / duration_months, 2)
    m = principal * (r / (1.0 - (1.0 + r) ** (-duration_months)))
    return round(m, 2)

def parse_power(details, full_text=""):
    """Extrait la puissance en kW et en Ch depuis les détails ou le texte complet."""
    for item in details:
        if item.get("ariaLabel") == "Puissance kW (CH)" or "kW" in str(item.get("data", "")):
            raw = str(item.get("data", ""))
            kw_match = re.search(r"(\d+)\s*kW", raw, re.IGNORECASE)
            ch_match = re.search(r"(\d+)\s*Ch|\b(\d+)\s*CV", raw, re.IGNORECASE)
            kw = int(kw_match.group(1)) if kw_match else None
            ch = int(ch_match.group(1) or ch_match.group(2)) if ch_match else None
            if kw or ch:
                if kw and not ch:
                    ch = round(kw * 1.35962)
                elif ch and not kw:
                    kw = round(ch / 1.35962)
                return kw, ch

    if full_text:
        kw_match = re.search(r"\b(\d{2,3})\s*kw\b", full_text, re.IGNORECASE)
        ch_match = re.search(r"\b(\d{2,3})\s*(?:ch|cv)\b", full_text, re.IGNORECASE)
        kw = int(kw_match.group(1)) if kw_match else None
        ch = int(ch_match.group(1)) if ch_match else None
        if kw and not ch:
            ch = round(kw * 1.35962)
        elif ch and not kw:
            kw = round(ch / 1.35962)
        if kw or ch:
            return kw, ch

    return None, None

def parse_km(details):
    """Extrait le kilométrage."""
    for item in details:
        if item.get("ariaLabel") == "Kilométrage" or "km" in str(item.get("data", "")):
            raw = str(item.get("data", ""))
            clean = re.sub(r"[^\d]", "", raw)
            if clean:
                return int(clean)
    return None

def parse_year(details):
    """Extrait l'année de première immatriculation."""
    for item in details:
        if item.get("ariaLabel") == "1ère immatriculation" or "/" in str(item.get("data", "")):
            raw = str(item.get("data", ""))
            year_match = re.search(r"\b(20\d{2})\b", raw)
            if year_match:
                return int(year_match.group(1))
    return None

def fetch_autoscout_listings(model_conf):
    """Récupère les annonces AutoScout24 pour un modèle donné."""
    url = model_conf["url"]
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        
        soup = BeautifulSoup(r.text, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script or not script.string:
            return []
            
        data = json.loads(script.string)
        listings = data.get("props", {}).get("pageProps", {}).get("listings", [])
        for it in listings:
            it["source"] = "AutoScout24"
        return listings
    except Exception as e:
        print(f"Erreur AutoScout24 pour {model_conf['name']}: {e}")
        return []

def evaluate_and_filter(raw_listings, model_conf, financial_conf, criteria_conf, history):
    """Filtre, évalue et enrichit les annonces selon les critères stricts et financiers."""
    matched = []
    now_str = datetime.now().isoformat()
    
    annual_rate = financial_conf["taux_taeg_annuel"] # 4.35% BoursoBank
    duration = financial_conf["duree_mois"] # 72 mois
    mens_max = financial_conf["mensualite_max"] # 300.0 €
    apport_5k = financial_conf["apport_min"] # 5000.0 €
    apport_7k = financial_conf["apport_max"] # 7000.0 €
    repat_cost = financial_conf.get("cout_rapatriement_estime", 350.0)

    max_km = criteria_conf.get("max_km", 100000)

    # Propriétés matériel / logistique du modèle (spécificités LM Music / Bastien)
    trunk_liters = model_conf.get("trunk_liters")
    has_v2l = model_conf.get("has_v2l", False)
    v2l_power = model_conf.get("v2l_power", "")
    has_kw_display = model_conf.get("has_kw_display", True)
    has_pac = model_conf.get("has_pac", False)

    for item in raw_listings:
        ad_id = item.get("id")
        if not ad_id:
            continue
            
        price_raw = item.get("price", {}).get("priceRaw")
        if not price_raw or price_raw <= 0:
            continue

        details = item.get("vehicleDetails", [])
        kw, ch = parse_power(details)
        km = parse_km(details)
        year = parse_year(details)
        
        title = item.get("title") or ""
        subtitle = item.get("subtitle") or ""
        source = item.get("source", "AutoScout24")

        # Construction exhaustive du texte complet pour filtrage ultra-précis
        v_obj = item.get("vehicle", {}) if isinstance(item.get("vehicle"), dict) else {}
        url_text = item.get("url", "").replace("-", " ").replace("/", " ")
        version_input = v_obj.get("modelVersionInput") or subtitle or ""
        motor_type = v_obj.get("motorTypeName", "")
        v_sub = v_obj.get("subtitle", "")
        v_variant = v_obj.get("variant", "")
        v_details_text = " ".join([str(d.get("data", "")) for d in details if isinstance(d, dict)])
        
        full_text = f"{title} {subtitle} {version_input} {motor_type} {v_sub} {v_variant} {url_text} {v_details_text}".lower()

        kw, ch = parse_power(details, full_text)
        km = parse_km(details)
        year = parse_year(details)
        
        # 1. Règle stricte : élimination si kilométrage > 100 000 km
        if km and km > max_km:
            continue

        # 2. Vérification de l'année minimale du modèle
        min_year = model_conf.get("min_year")
        if min_year and year and year < min_year:
            continue

        # 3. Mots-clés éliminatoires stricts (ex: thermiques, hybrides, petites batteries, finitions d'entrée)
        exclude_words = model_conf.get("keywords_exclude", [])
        if any(w.lower() in full_text for w in exclude_words):
            continue

        # 4. Mots-clés obligatoires stricts (si configurés, au moins un mot-clé requis doit être présent)
        keywords_must = model_conf.get("keywords_must", [])
        if keywords_must:
            if not any(k.lower() in full_text for k in keywords_must):
                continue

        # 5. Vérification de la puissance minimale (kW)
        min_power_kw = model_conf.get("min_power_kw")
        if min_power_kw and kw and kw < min_power_kw:
            continue

        # 6. Identification des finitions recherchées
        target_trims = model_conf.get("target_trims", [])
        detected_trims = [trim for trim in target_trims if trim.lower() in full_text]
        trim_label = " / ".join(detected_trims) if detected_trims else "À vérifier"

        # 6. Indicateurs de préférence utilisateur (2023-2025 et 50 000 - 60 000 km)
        is_recent = bool(year and year >= 2023)
        is_ideal_km = bool(km and km <= 60000)
        is_sweet_spot = bool(is_recent and is_ideal_km)

        # 7. Calculs financiers précis (BoursoBank 4,35 % sur 72 mois)
        total_price_key_in_hand = price_raw + repat_cost
        
        # Simulation avec apport 5 000 €
        loan_5k = max(0, total_price_key_in_hand - apport_5k)
        mens_5k = calculate_monthly_payment(loan_5k, annual_rate, duration)

        # Simulation avec apport 7 000 €
        loan_7k = max(0, total_price_key_in_hand - apport_7k)
        mens_7k = calculate_monthly_payment(loan_7k, annual_rate, duration)

        # Statut budgétaire
        if mens_5k <= mens_max:
            budget_status = "EXCELLENT_DEAL" # Rentrant direct avec 5k€ d'apport
            budget_badge = "Dans le budget (apport 5k€)"
            budget_class = "success"
        elif mens_7k <= mens_max:
            budget_status = "WITHIN_BUDGET" # Rentrant avec 7k€ d'apport
            budget_badge = "Dans le budget (apport 7k€)"
            budget_class = "info"
        elif mens_7k <= (mens_max + 25.0): # Dépasse de moins de 25€/mois (~1600€)
            budget_status = "NEGOTIABLE"
            budget_badge = "Négociable (< +25€/m)"
            budget_class = "warning"
        else:
            budget_status = "OVER_BUDGET"
            budget_badge = "Hors budget"
            budget_class = "danger"

        # 8. Scoring opportunité (sur 10)
        score = 4.0

        # Note Budget
        if budget_status == "EXCELLENT_DEAL":
            score += 2.5
        elif budget_status == "WITHIN_BUDGET":
            score += 1.5
        elif budget_status == "NEGOTIABLE":
            score += 0.5
        else:
            score -= 2.0

        # Bonus véhicules récents (2023 - 2025)
        if year:
            if year >= 2024:
                score += 2.0
            elif year == 2023:
                score += 1.5
            elif year == 2022:
                score += 0.5

        # Bonus kilométrage idéal (entre 35 000 et 60 000 km)
        if km:
            if 35000 <= km <= 60000:
                score += 2.0
            elif km < 35000:
                score += 1.8
            elif 60000 < km <= 80000:
                score += 0.6

        # Finition exacte détectée
        if detected_trims:
            score += 1.0

        # Bonus garantie Autohero ou bonne affaire
        if item.get("has_warranty"):
            score += 0.5

        score = max(1.0, min(10.0, round(score, 1)))

        # 9. Suivi historique (nouveauté / baisse de prix)
        is_new = False
        price_drop = 0
        if ad_id not in history:
            is_new = True
            history[ad_id] = {
                "first_seen": now_str,
                "initial_price": price_raw,
                "current_price": price_raw,
                "last_seen": now_str,
                "title": title
            }
        else:
            prev_price = history[ad_id].get("current_price", price_raw)
            if price_raw < prev_price:
                price_drop = prev_price - price_raw
            history[ad_id]["current_price"] = price_raw
            history[ad_id]["last_seen"] = now_str

        # Localisation & vendeur
        loc = item.get("location", {})
        if isinstance(loc, dict):
            city = loc.get("city", "France")
            zip_code = loc.get("zip", "")
        else:
            city = str(loc) if loc else "France"
            zip_code = ""

        seller = item.get("seller", {})
        if isinstance(seller, dict):
            seller_name = seller.get("name", "Pro")
            seller_type = "Pro" if seller.get("type") != "PRIVATE" else "Particulier"
        else:
            seller_name = "Autohero France" if source == "Autohero" else "Pro"
            seller_type = "Pro"

        # Image principale
        images = item.get("images", [])
        img_url = images[0] if images else ""

        # Lien complet
        rel_url = item.get("url", "")
        if rel_url.startswith("/fr/") and "autohero.com" not in rel_url and "autoscout24.fr" not in rel_url:
            ad_url = f"https://www.autohero.com{rel_url}" if source == "Autohero" else f"https://www.autoscout24.fr{rel_url}"
        elif rel_url.startswith("/"):
            ad_url = f"https://www.autoscout24.fr{rel_url}"
        else:
            ad_url = rel_url

        matched.append({
            "id": ad_id,
            "source": source,
            "model_id": model_conf["id"],
            "model_name": model_conf["name"],
            "title": title,
            "version_input": version_input,
            "price_raw": price_raw,
            "repat_cost": repat_cost,
            "total_price_key_in_hand": total_price_key_in_hand,
            "mens_5k": mens_5k,
            "mens_7k": mens_7k,
            "km": km,
            "year": year,
            "power_kw": kw,
            "power_ch": ch,
            "trim_label": trim_label,
            "has_target_trim": bool(detected_trims),
            "is_recent": is_recent,
            "is_ideal_km": is_ideal_km,
            "is_sweet_spot": is_sweet_spot,
            "trunk_liters": trunk_liters,
            "has_v2l": has_v2l,
            "v2l_power": v2l_power,
            "has_kw_display": has_kw_display,
            "has_pac": has_pac,
            "city": city,
            "zip": zip_code,
            "seller_name": seller_name,
            "seller_type": seller_type,
            "has_warranty": item.get("has_warranty", False),
            "warranty_text": item.get("warranty_text", ""),
            "img_url": img_url,
            "ad_url": ad_url,
            "score": score,
            "budget_status": budget_status,
            "budget_badge": budget_badge,
            "budget_class": budget_class,
            "is_new": is_new,
            "price_drop": price_drop,
            "updated_at": now_str
        })

    return matched

def run_watcher():
    config = load_config()
    history = load_history()
    all_matched = []

    print("=== Démarrage de la veille véhicules électriques multi-sources ===")
    print(f"Modèles surveillés : {len(config['models'])}")

    # 1. Scraping AutoScout24 par modèle
    print("\n--- 1. Extraction AutoScout24 ---")
    for model_conf in config["models"]:
        raw_listings = fetch_autoscout_listings(model_conf)
        matched = evaluate_and_filter(raw_listings, model_conf, config["financial"], config.get("criteria", {}), history)
        print(f"   -> [AutoScout24] Retenu pour {model_conf['name']} : {len(matched)} annonces qualifiées")
        all_matched.extend(matched)
        time.sleep(0.4)

    # 2. Scraping Autohero (véhicules reconditionnés avec garantie 1 an)
    print("\n--- 2. Extraction Autohero ---")
    try:
        autohero_raw = fetch_autohero_listings()
        print(f"   -> [Autohero] {len(autohero_raw)} annonces électriques brutes récupérées")
        
        # Dispatch par modèle configuré
        for auto_item in autohero_raw:
            hint_id = auto_item.get("model_id_hint")
            matching_conf = next((m for m in config["models"] if m["id"] == hint_id), None)
            if not matching_conf:
                # Recherche par titre
                title_lower = auto_item.get("title", "").lower()
                for m in config["models"]:
                    if any(k.lower() in title_lower for k in m.get("keywords_must", [])):
                        matching_conf = m
                        break
            
            if matching_conf:
                matched_auto = evaluate_and_filter([auto_item], matching_conf, config["financial"], config.get("criteria", {}), history)
                if matched_auto:
                    print(f"   -> [Autohero] Annonce qualifiée : {matched_auto[0]['title']} ({matched_auto[0]['price_raw']} €)")
                    all_matched.extend(matched_auto)
    except Exception as e:
        print(f"   -> Note Autohero : {e}")

    # 3. Traçabilité Spoticar & La Centrale
    print("\n--- 3. Statut Spoticar & La Centrale ---")
    print("   -> Spoticar & La Centrale sont protégés par pare-feu anti-bot (Akamai Edge / DataDome).")
    print("   -> Des liens directs de recherche pré-paramétrés sont intégrés au dashboard pour un accès immédiat.")

    save_history(history)

    # Tri global de toutes les annonces : meilleures notes et mensualité la plus basse en premier
    all_matched.sort(key=lambda x: (-x["score"], x["mens_7k"]))

    # Calcul des statistiques de marché et de la courbe prévisionnelle arrêtée en Mai 2027
    trends_data = compute_model_statistics_and_forecast(all_matched, config)

    # Sauvegarde des résultats
    results_data = {
        "generated_at": datetime.now().isoformat(),
        "total_analyzed": len(all_matched),
        "in_budget_count": len([x for x in all_matched if x["budget_status"] in ["EXCELLENT_DEAL", "WITHIN_BUDGET"]]),
        "negotiable_count": len([x for x in all_matched if x["budget_status"] == "NEGOTIABLE"]),
        "new_count": len([x for x in all_matched if x["is_new"]]),
        "price_drop_count": len([x for x in all_matched if x["price_drop"] > 0]),
        "trends": trends_data,
        "listings": all_matched
    }

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)

    # Génération du dashboard HTML
    html_content = build_html(results_data, config)
    with open(REPORT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✓ Rapport HTML généré avec succès : {REPORT_HTML_PATH}")
    print(f"✓ Total : {results_data['total_analyzed']} annonces ({results_data['in_budget_count']} dans le budget, {results_data['negotiable_count']} négociables)")
    
    return results_data

if __name__ == "__main__":
    run_watcher()
