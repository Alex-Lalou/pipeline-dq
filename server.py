"""
Pipeline Doc + DQ Analyzer — Proxy FastAPI
==========================================
Usage:
    pip install fastapi uvicorn httpx python-dotenv
    export ANTHROPIC_API_KEY=sk-ant-...
    python server.py

Le frontend HTML se connecte à ce serveur local au lieu d'appeler
Anthropic directement — la clé API ne sort jamais du serveur.
"""

import os
import httpx
import logging
import time
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Rate limiting simple en mémoire (par IP)
RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "20"))  # max 20 requêtes/minute par IP
_rate_store = defaultdict(list)

def check_rate_limit(client_ip: str):
    now = time.time()
    window = 60  # 1 minute
    _rate_store[client_ip] = [t for t in _rate_store[client_ip] if now - t < window]
    if len(_rate_store[client_ip]) >= RATE_LIMIT_RPM:
        raise HTTPException(
            status_code=429,
            detail=f"Trop de requêtes — limite : {RATE_LIMIT_RPM} req/min."
        )
    _rate_store[client_ip].append(now)
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

if not ANTHROPIC_API_KEY:
    print("⚠️  ATTENTION : variable ANTHROPIC_API_KEY non définie.")
    print("   Lancez : export ANTHROPIC_API_KEY=sk-ant-...")

app = FastAPI(title="Pipeline DQ Proxy", version="1.0.0")

# CORS — restreint par défaut, configurable via variable d'env ALLOWED_ORIGINS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "X-Access-Token"],
)


@app.get("/health")
def health():
    """Vérification que le serveur tourne."""
    return {
        "status": "ok",
        "api_key_configured": bool(ANTHROPIC_API_KEY),
    }


# Token d'accès optionnel (recommandé en prod) — configurable via ACCESS_TOKEN
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

def check_auth(request: Request):
    if not ACCESS_TOKEN:
        return  # Pas de token configuré = accès libre (dev local)
    token = request.headers.get("X-Access-Token", "")
    if token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Token d'accès invalide.")

MAX_PAYLOAD_BYTES = 512 * 1024  # 512 Ko max

@app.post("/api/analyse")
async def analyse(request: Request):
    """
    Proxy sécurisé vers Anthropic API.
    - Auth par token (optionnel)
    - Limite de taille du payload
    - Validation minimale du body
    - Clé API stockée côté serveur uniquement
    """
    check_auth(request)
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    if not ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Clé API Anthropic non configurée sur le serveur."
        )

    # Limiter la taille du payload
    body_bytes = await request.body()
    if len(body_bytes) > MAX_PAYLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"Payload trop grand (max {MAX_PAYLOAD_BYTES//1024} Ko).")

    try:
        body = __import__('json').loads(body_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="Body JSON invalide.")

    # Validation de schéma stricte
    if "model" not in body or "messages" not in body:
        raise HTTPException(status_code=400, detail="Champs 'model' et 'messages' requis.")
    if not isinstance(body["messages"], list) or len(body["messages"]) == 0:
        raise HTTPException(status_code=400, detail="'messages' doit être une liste non vide.")
    if len(body["messages"]) > 10:
        raise HTTPException(status_code=400, detail="Trop de messages (max 10).")
    # Autoriser uniquement les modèles Anthropic connus
    allowed_models = {"claude-sonnet-4-6", "claude-opus-4-6", "claude-haiku-4-5-20251001"}
    if body.get("model") not in allowed_models:
        raise HTTPException(status_code=400, detail=f"Modèle non autorisé : {body.get('model')}")

    async with httpx.AsyncClient(timeout=200.0) as client:
        response = await client.post(
            ANTHROPIC_URL,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": ANTHROPIC_VERSION,
            },
            json=body,
        )

    if response.status_code == 401:
        raise HTTPException(status_code=502, detail="Clé API Anthropic invalide ou expirée.")
    elif response.status_code == 429:
        raise HTTPException(status_code=429, detail="Quota API Anthropic dépassé — réessayez dans quelques instants.")
    elif response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Erreur Anthropic ({response.status_code}) : {response.text[:200]}"
        )

    logger.info(f"Proxy Anthropic OK — {response.status_code} — {len(body_bytes)} bytes")
    return response.json()


# Servir les librairies JS locales si présentes dans ./static/
import os as _os
_static_dir = _os.path.join(_os.path.dirname(__file__), "static")
if _os.path.exists(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

# Servir le fichier HTML statique si présent dans le même dossier
@app.get("/")
def serve_frontend():
    html_path = os.path.join(os.path.dirname(__file__), "pipeline_doc_dq_tool_client.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Frontend non trouvé. Placez pipeline_doc_dq_tool.html dans le même dossier."}


if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("  Pipeline Doc + DQ Analyzer — Serveur proxy")
    print("=" * 55)
    print(f"  Clé API   : {'✓ configurée' if ANTHROPIC_API_KEY else '✗ MANQUANTE'}")
    print(f"  Rate limit: {RATE_LIMIT_RPM} req/min/IP")
    print(f"  CORS      : {ALLOWED_ORIGINS}")
    print(f"  URL       : http://localhost:8000")
    print(f"  Health    : http://localhost:8000/health")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
