# BuffettValue — V1 en développement

## Interface DCF locale (recherche uniquement)

Prérequis : Python 3.10+ ; aucune dépendance externe pour le calculateur.

```bash
python3 -m buffettvalue.web --port 8765
```

Ouvrir http://127.0.0.1:8765 ; saisir les hypothèses de flux de trésorerie, croissance, actualisation, croissance terminale, dette nette, actions et cours. Le serveur écoute uniquement sur 127.0.0.1.

Mode ligne de commande :

```bash
python3 -m buffettvalue --input examples/dcf-example.json
python3 -m unittest discover -s tests -v
```

**Limites bloquantes pour la V1 complète :** chiffres manuels non datés et non certifiés ; pas encore d'ingestion SEC, d'analyse historique 5–10 ans, de suivi de portefeuille ni d'ordres PAPER. L'interface ne donne aucun signal d'achat automatisé.

## Import d'un fichier SEC Company Facts

Télécharger le fichier JSON officiel d'une entreprise depuis `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` (CIK sur 10 chiffres), conformément aux conditions SEC et avec une identification User-Agent appropriée. Aucun téléchargement automatisé n'est encore implémenté.

```bash
python3 -m buffettvalue.sec_cli --input /chemin/vers/CIK##########.json --as-of 2026-06-30
```

Le rapport affiche les flux de trésorerie annuels, les investissements, le FCF calculé, les dates de dépôt SEC et le nombre d'actions publié. Les données déposées après `--as-of` sont exclues. Cette première version ne traite que les formulaires 10-K/10-K/A et les tags US-GAAP principaux ; elle ne couvre pas toutes les entreprises ni toutes les variantes XBRL. **Aucun signal d'achat ou ordre PAPER n'est autorisé sur cette seule base.**
