#!/usr/bin/env python3
"""
Module d'alerte et de notification optionnelle (Discord / Telegram / Console)
"""

import json
import os
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(BASE_DIR, "results.json")

def send_notifications():
    if not os.path.exists(RESULTS_PATH):
        return

    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = data.get("total_analyzed", 0)
    in_budget = data.get("in_budget_count", 0)
    negotiable = data.get("negotiable_count", 0)
    listings = data.get("listings", [])

    top_deals = listings[:5]

    # Construction du message texte
    lines = [
        "⚡ **Surveillance Marché VE — Rapport Tous les 3 Jours** ⚡",
        f"📊 **Bilan :** {total} annonces analysées (< 100k km)",
        f"🟢 **Dans le budget (≤ 300 €/m BoursoBank) :** {in_budget}",
        f"🟡 **À négocier (< +25 €/m) :** {negotiable}",
        "",
        "🎯 **Top 5 Meilleures Opportunités :**"
    ]

    for i, c in enumerate(top_deals, 1):
        flag = "🎯 " if c.get("is_sweet_spot") else ""
        km_str = f"{c.get('km', 0):,} km".replace(",", " ")
        lines.append(
            f"{i}. {flag}**{c['model_name']}** ({c.get('year', '-')}) — **{c['price_raw']:,} €**\n"
            f"   • Mensualité BoursoBank : **{c['mens_7k']} €/m** (apport 7k€)\n"
            f"   • {km_str} | 📍 {c.get('city', 'France')}\n"
            f"   • Lien : {c['ad_url']}"
        )

    message_text = "\n".join(lines)

    # 1. Discord Webhook
    discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if discord_webhook:
        try:
            payload = {
                "content": message_text[:1950]
            }
            r = requests.post(discord_webhook, json=payload, timeout=10)
            print(f"Notification Discord envoyée (status {r.status_code})")
        except Exception as e:
            print(f"Erreur notification Discord : {e}")

    # 2. Telegram Bot
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if telegram_token and telegram_chat_id:
        try:
            tg_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            payload = {
                "chat_id": telegram_chat_id,
                "text": message_text,
                "disable_web_page_preview": True
            }
            r = requests.post(tg_url, json=payload, timeout=10)
            print(f"Notification Telegram envoyée (status {r.status_code})")
        except Exception as e:
            print(f"Erreur notification Telegram : {e}")

if __name__ == "__main__":
    send_notifications()
