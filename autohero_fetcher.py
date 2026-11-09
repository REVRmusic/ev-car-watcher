#!/usr/bin/env python3
"""
Autohero Fetcher - Module d'extraction des annonces Autohero pour EV Car Watcher
Extrait les données structurées schema.org (Product et Vehicle) pour les véhicules 100% électriques.
"""

import json
import logging
import re
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Modèles ciblés et leurs correspondances chez Autohero
AUTOHERO_QUERIES = [
    {
        "brand": "skoda",
        "model": "enyaq",
        "model_id": "skoda_enyaq_80",
        "kw_must": ["80", "85"],
        "kw_exclude": ["iv 50", "iv 60", " 50 ", " 60 "]
    },
    {
        "brand": "renault",
        "model": "megane",
        "model_id": "megane_etech_iconic",
        "kw_must": ["megane", "e-tech", "ev60"],
        "kw_exclude": ["ev40", "130 ch", "tce", "dci", "hybrid", "hybride"]
    },
    {
        "brand": "kia",
        "model": "ev6",
        "model_id": "kia_ev6",
        "kw_must": ["ev6", "77"],
        "kw_exclude": ["58 kwh", "170 ch"]
    },
    {
        "brand": "kia",
        "model": "niro",
        "model_id": "kia_niro_ev_premium",
        "kw_must": ["niro", "64", "electrique"],
        "kw_exclude": ["hybride", "phev", "gdi", "hev", "motion"]
    },
    {
        "brand": "hyundai",
        "model": "ioniq-5",
        "model_id": "hyundai_ioniq_5",
        "kw_must": ["ioniq", "5"],
        "kw_exclude": ["58 kwh", "crdi", "hybrid"]
    },
    {
        "brand": "hyundai",
        "model": "kona",
        "model_id": "hyundai_kona_2_exec",
        "kw_must": ["kona", "65", "electrique"],
        "kw_exclude": ["39 kwh", "48 kwh", "hybrid", "hybride", "crdi", "gdi"]
    },
    {
        "brand": "ford",
        "model": "mustang-mach-e",
        "model_id": "mustang_mache_er",
        "kw_must": ["mustang", "mach-e"],
        "kw_exclude": ["standard range", "sr", "70 kwh", "75 kwh"]
    },
    {
        "brand": "byd",
        "model": "seal-u",
        "model_id": "byd_seal_u_design",
        "kw_must": ["seal", "design"],
        "kw_exclude": ["dm-i", "hybride", "comfort"]
    },
    {
        "brand": "peugeot",
        "model": "3008",
        "model_id": "peugeot_e3008_gt",
        "kw_must": ["e-3008", "electrique", "73", "gt"],
        "kw_exclude": ["puretech", "blue-hdi", "hdi", "hybrid", "hybride", "allure"]
    },
]

def fetch_autohero_detail(url):
    """Extrait les informations détaillées d'une fiche véhicule Autohero."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        for s in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(s.string)
                if data.get("@type") == "Vehicle":
                    fuel = str(data.get("vehicleEngine", {}).get("fuelType", "")).lower()
                    if "électrique" in fuel or "electrique" in fuel or "electric" in fuel:
                        return data
            except Exception:
                continue
    except Exception as e:
        logger.warning(f"Erreur fetch detail Autohero {url}: {e}")
    return None

def fetch_autohero_listings():
    """
    Récupère et normalise l'ensemble des annonces électriques pertinentes sur Autohero.
    """
    all_raw_listings = []
    seen_urls = set()

    for q in AUTOHERO_QUERIES:
        brand = q["brand"]
        model = q["model"]
        url = f"https://www.autohero.com/fr/search/?brand={brand}&model={model}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            for s in soup.find_all("script"):
                text = s.string or ""
                if '"@type":"Product"' in text:
                    try:
                        p = json.loads(text)
                        p_url = p.get("url")
                        if not p_url or p_url in seen_urls:
                            continue
                        
                        full_name = f"{p.get('name', '')} {p.get('description', '')}".lower()

                        if any(ex in full_name for ex in q["kw_exclude"]):
                            continue

                        if any(must in full_name for must in q["kw_must"]):
                            seen_urls.add(p_url)
                            detail = fetch_autohero_detail(p_url)
                            if detail:
                                listing = normalize_autohero_listing(detail, p, q["model_id"])
                                if listing:
                                    all_raw_listings.append(listing)
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Erreur requête Autohero {brand} {model}: {e}")

    try:
        gen_url = "https://www.autohero.com/fr/search/?fuelType=ELECTRIC"
        r = requests.get(gen_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for s in soup.find_all("script"):
                text = s.string or ""
                if '"@type":"Product"' in text:
                    try:
                        p = json.loads(text)
                        p_url = p.get("url")
                        if not p_url or p_url in seen_urls:
                            continue
                        full_name = f"{p.get('name', '')} {p.get('description', '')}".lower()
                        
                        for q in AUTOHERO_QUERIES:
                            if any(ex in full_name for ex in q["kw_exclude"]):
                                continue
                            if any(must in full_name for must in q["kw_must"]):
                                seen_urls.add(p_url)
                                detail = fetch_autohero_detail(p_url)
                                if detail:
                                    listing = normalize_autohero_listing(detail, p, q["model_id"])
                                    if listing:
                                        all_raw_listings.append(listing)
                                break
                    except Exception:
                        continue
    except Exception as e:
        logger.warning(f"Erreur recherche globale Autohero: {e}")

    return all_raw_listings

def normalize_autohero_listing(v, product, target_model_id):
    """
    Normalise les données du Vehicle Schema Autohero au format de l'application.
    """
    try:
        sku = v.get("sku") or product.get("productID") or re.sub(r"[^\w]", "", v.get("offers", {}).get("url", ""))[-12:]
        url = v.get("offers", {}).get("url") or product.get("url")
        price = v.get("offers", {}).get("price")
        if not price or price <= 0:
            return None

        km_str = str(v.get("mileageFromOdometer", ""))
        km_clean = re.sub(r"[^\d]", "", km_str)
        km = int(km_clean) if km_clean else None

        first_reg = str(v.get("dateVehiclefirstregistered", ""))
        year_match = re.search(r"\b(20\d{2})\b", first_reg)
        year = int(year_match.group(1)) if year_match else None

        eng = v.get("vehicleEngine", {})
        eng_power = str(eng.get("enginePower", ""))
        kw_match = re.search(r"(\d+)\s*kW", eng_power, re.IGNORECASE)
        ch_match = re.search(r"(\d+)\s*CV|ch", eng_power, re.IGNORECASE)
        kw = int(kw_match.group(1)) if kw_match else None
        ch = int(ch_match.group(1)) if ch_match else None

        name = v.get("name") or product.get("name")
        description = v.get("description") or product.get("description")
        image = v.get("image") or product.get("image")
        if image and "{size}" in image:
            image = image.replace("{size}", "768x432-")

        vehicle_details = []
        if kw or ch:
            vehicle_details.append({"ariaLabel": "Puissance kW (CH)", "data": f"{kw or ''} kW ({ch or ''} Ch)"})
        if km:
            vehicle_details.append({"ariaLabel": "Kilométrage", "data": f"{km:,} km".replace(",", " ")})
        if year:
            vehicle_details.append({"ariaLabel": "1ère immatriculation", "data": str(year)})

        return {
            "id": f"autohero_{sku}",
            "source": "Autohero",
            "model_id_hint": target_model_id,
            "title": name,
            "subtitle": description,
            "url": url,
            "price": {
                "priceRaw": int(price),
                "priceEvaluation": 1,
            },
            "vehicleDetails": vehicle_details,
            "images": [image] if image else [],
            "location": "Autohero France (Reconditionné)",
            "has_warranty": True,
            "warranty_text": "Garantie 1 an & 21 jours satisfait ou remboursé",
        }
    except Exception as e:
        logger.warning(f"Erreur normalisation Autohero: {e}")
        return None
