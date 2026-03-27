# Pipeline Doc + DQ Analyzer — Installation client

## Prérequis
- Python 3.9+
- Accès internet vers api.anthropic.com (uniquement pour le mode Code)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

```bash
# Linux / Mac
export ANTHROPIC_API_KEY=sk-ant-votre-cle-ici

# Windows
set ANTHROPIC_API_KEY=sk-ant-votre-cle-ici
```

Ou créer un fichier `.env` dans le même dossier :
```
ANTHROPIC_API_KEY=sk-ant-votre-cle-ici
```

## Lancement

```bash
python server.py
```

Puis ouvrir dans le navigateur :  
**http://localhost:8000**

## Mode GitHub Pages (Nexialog interne)

L'outil fonctionne aussi directement sur GitHub Pages sans serveur,
avec la clé API saisie dans l'interface.
Ce mode est réservé à l'usage interne Nexialog.

## Ce qui transite par le serveur

| Fonctionnalité | Transite par serveur | Données envoyées |
|---|---|---|
| Analyse de code (Mode Code) | ✓ Oui | Le code source uniquement |
| Profiling DQ (Mode Données) | ✗ Non | Rien — 100% local |
| Comparaison arrêtés | ✗ Non | Rien — 100% local |
| Export Excel / PDF | ✗ Non | Rien — 100% local |

**Les données client ne sortent jamais du navigateur.**
