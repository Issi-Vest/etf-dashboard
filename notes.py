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
ALERTES = ["Test d'alerte"]

MEMO = """
Si -20%/+haut du trimestre alors réinvestir sur 10 semaines.
Si cassure de trendline => alléger.
Quand tout est euphorique, il faut sortir. Dans la panique, il faut entrer.
Etre en position que quand tendance haussière, sinon le monétaire rapporte mieux !
En range, on gagne plus d'argent sur du monétaire que sur des actifs qui stagnent.
"""

# Fundsmith : utilisé seulement si le site refuse la requête automatique.
# À mettre à jour une fois par mois.
FUNDSMITH_MOIS = "Octobre 2026"
FUNDSMITH_TOP10 = ["Waters", "Visa", "Mastercard", "Amadeus", "Veeva Systems",
                   "Stryker", "L'Oréal", "Yum! Brands", "Church & Dwight", "Sage"]
FUNDSMITH_COMMENTAIRE = """There were no outright sales or purchases of holdings made in the month. The top 5 contributors in the month were Sage, Mastercard, Visa, Church & Dwight and Veeva Systems. The top 5 detractors were Fortinet, Meta Platforms, Alphabet, TSMC and Legrand."""
