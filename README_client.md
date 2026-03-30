# Pipeline Doc + DQ Analyzer — Version Client Banque

## Deux versions disponibles

| Version | Fichier | Usage | Clé API |
|---|---|---|---|
| **Interne Nexialog** | `pipeline_doc_dq_tool.html` | GitHub Pages, usage consultant | Saisie dans l'interface |
| **Client banque** | `pipeline_doc_dq_tool_client.html` | Serveur client, données sensibles | Stockée côté serveur uniquement |

---

## Installation version client

### 1. Prérequis
- Python 3.9+
- Accès sortant vers `api.anthropic.com` (uniquement pour le mode Code IA)

### 2. Installation des dépendances Python
```bash
pip install -r requirements.txt
```

### 3. Téléchargement des librairies JS (optionnel — mode hors-ligne)
```bash
python download_libs.py
```
Les librairies sont placées dans `./static/`. L'outil les chargera localement sans accès internet.

### 4. Configuration
```bash
# Obligatoire
export ANTHROPIC_API_KEY=sk-ant-votre-cle

# Optionnel — sécurité renforcée
export ACCESS_TOKEN=mon-token-secret       # Token d'accès au proxy
export ALLOWED_ORIGINS=http://monserveur   # CORS (défaut: localhost uniquement)
export RATE_LIMIT_RPM=20                   # Requêtes max/min/IP (défaut: 20)
```

Ou créer un fichier `.env` :
```
ANTHROPIC_API_KEY=sk-ant-votre-cle
ACCESS_TOKEN=mon-token-secret
ALLOWED_ORIGINS=http://monserveur.banque.fr,http://localhost:8000
```

### 5. Lancement
```bash
python server.py
```

Puis ouvrir : **http://localhost:8000**

---

## Ce qui transite par le serveur

| Fonctionnalité | Données envoyées |
|---|---|
| ⟨/⟩ Analyse de code | Code source → proxy → Anthropic |
| ⊞ Profilage DQ | **Rien** — 100% local navigateur |
| ⇄ Comparaison arrêtés | **Rien** — 100% local navigateur |
| Export Excel / PDF | **Rien** — 100% local navigateur |

**Les données client ne quittent jamais le navigateur.**

---

## Architecture sécurité

```
Navigateur
    │
    ├── DQ / Comparaison / Export ──→ 100% local
    │
    └── Analyse de code ──→ http://localhost:8000/api/analyse
                                    │  ✓ CORS restreint
                                    │  ✓ Auth token (optionnel)
                                    │  ✓ Limite payload 512 Ko
                                    │  ✓ Validation schéma JSON
                                    │  ✓ Rate limiting 20 req/min/IP
                                    │  ✓ Whitelist modèles Anthropic
                                    │  ✓ Logging horodaté
                                    └── api.anthropic.com
                                        (clé API côté serveur uniquement)
```

---

## Ce qui n'est PAS dans cette version client
- ❌ Saisie de clé API dans l'interface
- ❌ Stockage de clé en localStorage
- ❌ Appel direct à Anthropic depuis le navigateur

