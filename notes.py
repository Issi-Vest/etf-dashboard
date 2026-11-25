# Rappels affichés sous les graphiques.
# Clé = le nom affiché sur la page (sans l'emoji), valeur = le texte.
# Chaque ligne se termine par une virgule.
# \n = retour à la ligne.
NOTES = {
    "XAUUSD": "Si USD monte, l'or baisse !",
    "USDEUR": "Si USD baisse, l'or monte !",
    "DXY" : "Analyser le DXY pour savoir si c'est le $ qui varie ou si c'est l'€",
    "DBC": "Énergie dominante (plafond ~60%), reste en métaux et agriculture",
    "COMO": "Énergie ~45% / Métaux industriels ~33% / Métaux précieux ~22% - Pas d'agriculture !",
    "ICOM": "Agriculture ~30% / Énergie ~27% / Métaux ind. ~18% / Métaux préc. ~16% / Élevage ~7%",
    "SP500": "Acheter sur support TACO avril 2025 !"
}

# Alertes affichées tout en haut de la page (une phrase par ligne).
ALERTES = ["Garder un portefeuille équilibré !"]

# Mémo affiché tout en haut de la page
MEMO = """
Si -20%/+haut du trimestre alors réinvestir sur 10 semaines.
Si cassure de trendline => alléger.
Quand tout est euphorique, il faut sortir. Dans la panique, il faut entrer.
Etre en position que quand tendance haussière, sinon le monétaire rapporte mieux !
En range, on gagne plus d'argent sur du monétaire que sur des actifs qui stagnent.

(Notes manuelles (alertes, mémo, notes) à écrire dans notes.py)
(Notes concernant le renouvellement du jeton "actualiser" dans notes.py)
"""

# Fundsmith : utilisé seulement si le site refuse la requête automatique.
# À mettre à jour une fois par mois.
FUNDSMITH_MOIS = "Octobre 2026"
FUNDSMITH_TOP10 = ["Waters", "Visa", "Mastercard", "Amadeus", "Veeva Systems",
                   "Stryker", "L'Oréal", "Yum! Brands", "Church & Dwight", "Sage"]
FUNDSMITH_COMMENTAIRE = """There were no outright sales or purchases of holdings made in the month. The top 5 contributors in the month were Sage, Mastercard, Visa, Church & Dwight and Veeva Systems. The top 5 detractors were Fortinet, Meta Platforms, Alphabet, TSMC and Legrand."""

# =====================================================
# RENOUVELER LE JETON DU BOUTON "ACTUALISER" (tous les ~90 jours)
# Signe que c'est nécessaire : le bouton affiche "Erreur 401".
# =====================================================
# 1. Aller sur github.com, cliquer sur l'avatar (en haut à droite)
#    puis "Settings" (les réglages du COMPTE, pas ceux du repo).
# 2. Tout en bas du menu de gauche : "Developer settings".
# 3. "Personal access tokens" -> "Tokens (classic)".
# 4. "Generate new token" -> "Generate new token (classic)".
# 5. Nom : dashboard-trigger / Expiration : 90 jours.
# 6. Cocher UNIQUEMENT la case "workflow", puis "Generate token".
# 7. COPIER le jeton tout de suite (il commence par ghp_ et ne sera
#    plus jamais affiché). Ne le coller nulle part d'autre.
# 8. Aller dans le repo etf-dashboard -> Settings
#    -> "Secrets and variables" -> "Actions".
# 9. Repérer le secret DISPATCH_TOKEN -> cliquer sur le crayon
#    ("Update secret") -> coller le nouveau jeton -> "Update secret".
# 10. (Facultatif) Supprimer l'ancien jeton dans Developer settings.
# 11. Onglet Actions -> "ETF Dashboard" -> "Run workflow", pour que la
#     page se régénère avec le nouveau jeton. Ensuite, tester le
#     bouton "Actualiser" : il doit afficher "Lancé".
