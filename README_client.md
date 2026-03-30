# Pipeline Doc + DQ Analyzer — Version Client

## Deux versions disponibles

| Version | Fichier | Usage | Clé API |
|---|---|---|---|
| **Interne Nexialog** | `pipeline_doc_dq_tool.html` | GitHub Pages, usage consultant | Saisie dans l'interface |
| **Client banque** | `pipeline_doc_dq_tool_client.html` | Serveur client, données sensibles | Stockée côté serveur |

---

## Installation version client

### 1. Prérequis
- Python 3.9+
- Accès sortant vers `api.anthropic.com` (uniquement pour le mode Code)

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Configuration de la clé API
```bash
# Linux / Mac
export ANTHROPIC_API_KEY=sk-ant-votre-cle

# Windows
set ANTHROPIC_API_KEY=sk-ant-votre-cle
```

Ou créer un fichier `.env` :
```
ANTHROPIC_API_KEY=sk-ant-votre-cle
```

### 4. Lancement
```bash
python server.py
```

Puis ouvrir : **http://localhost:8000**

---

## Ce qui transite par le serveur

| Fonctionnalité | Données envoyées à Anthropic |
|---|---|
| ⟨/⟩ Analyse de code | Le code source uniquement |
| ⊞ Profilage DQ | **Rien** — 100% local navigateur |
| ⇄ Comparaison arrêtés | **Rien** — 100% local navigateur |
| Export Excel / PDF | **Rien** — 100% local navigateur |

**Les données client ne quittent jamais le navigateur.**

---

## Architecture sécurité

```
Navigateur client
    │
    ├── DQ / Comparaison / Export ──→ 100% local (pas de réseau)
    │
    └── Analyse de code ──→ http://localhost:8000/api/analyse
                                    │
                                    └── Anthropic API
                                        (clé stockée serveur)
```

### Différences avec la version interne
- Clé API **jamais** exposée côté navigateur
- Bannière de saisie de clé supprimée
- Détection automatique si le serveur proxy est joignable
- `localStorage` désactivé pour la clé

