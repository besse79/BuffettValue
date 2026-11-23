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
