# ⚡ Surveillance Marché Véhicules Électriques

Système autonome de veille du marché des véhicules d'occasion électriques avec simulation de financement en temps réel, observatoire des fourchettes de prix et courbes prévisionnelles de décote.

---

## 🎯 Modèles Surveillés
1. **Renault Mégane E-Tech** (Iconic - Optimum Charge AC 22 kW / DC 130 kW - EV60 220 ch)
2. **Kia Niro EV 64,8 kWh** (Finition haut de gamme Premium)
3. **Skoda Enyaq iV 80** (Batterie 77 kWh utiles - Loft Pack Confort ou Sportline)
4. **Hyundai Ioniq 5** (Batterie 73/77 kWh - Finitions Creative ou Executive)
5. **Kia EV6 Grande Autonomie** (Batterie 77,4 kWh - Finitions Air Design ou GT-Line)
6. **Ford Mustang Mach-E** (Extended Range 88/91 kWh utiles)
7. **Hyundai Kona 2 Grande Autonomie** (Batterie 65 kWh - Finition Executive 2023+)
8. **Peugeot e-3008** (Batterie 73 kWh - Finition GT 2024+)
9. **BYD Seal U EV** (Batterie Blade LFP 87 kWh - Finition Design)

---

## 💰 Barème Financement & Filtres Stricts
* **Financement :** BoursoBank Prêt Éco-responsable Véhicule Propre (4,35 % TAEG fixe avec justificatif).
* **Durée :** 72 mois (6 ans).
* **Mensualité cible maximale :** ≤ 300 € / mois.
* **Apport simulé :** 5 000 € à 7 000 €.
* **Rapatriement inclus :** ~350 € réservés dans le calcul clé en main.
* **Règle Kilométrage :** Exclusion stricte au-delà de 100 000 km (Zone idéale : 50 000 - 60 000 km).
* **Règle Millésime :** Priorité forte donnée aux millésimes récents (2023 - 2025).

---

## 🤖 Fonctionnement 100% Autonome (GitHub Actions)
Le workflow [`.github/workflows/car_watcher.yml`](.github/workflows/car_watcher.yml) s'exécute automatiquement **tous les 3 jours à 07:00 UTC (08:00/09:00 Paris)** même si votre ordinateur est éteint :
1. Analyse l'ensemble du marché et extrait les annonces qualifiées.
2. Identifie les nouvelles annonces et les baisses de prix.
3. Consigne les statistiques dans `market_trends.json` pour suivre la décote réelle.
4. Génère le tableau de bord interactif `index.html` (avec graphiques Chart.js de projection sur 24 mois).
5. Sauvegarde automatiquement les données sur le dépôt.

---

## 🌐 Consultation du Tableau de Bord en Ligne (GitHub Pages)
Pour consulter votre tableau de bord directement depuis votre smartphone ou navigateur :
1. Rendez-vous sur votre dépôt GitHub dans **Settings** > **Pages**.
2. Sous **Build and deployment**, sélectionnez la branche `main` et le dossier `/ (root)`.
3. Cliquez sur **Save**.
4. Votre tableau de bord sera accessible publiquement ou en privé à l'adresse :  
   `https://<votre-pseudo-github>.github.io/<nom-du-repo>/`

---

## 📲 Notifications Smartphone (Optionnel)
Pour recevoir le récapitulatif directement sur votre téléphone tous les 3 jours :
* **Discord :** Ajoutez l'URL de votre Webhook dans les secrets du dépôt sous le nom `DISCORD_WEBHOOK_URL`.
* **Telegram :** Ajoutez `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` dans les secrets du dépôt.
