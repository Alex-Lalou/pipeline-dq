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

# Autoriser les requêtes depuis le navigateur (GitHub Pages ou local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restreindre en production à votre domaine
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Vérification que le serveur tourne."""
    return {
        "status": "ok",
        "api_key_configured": bool(ANTHROPIC_API_KEY),
    }


@app.post("/api/analyse")
async def analyse(request: Request):
    """
    Proxy vers Anthropic API.
    Reçoit le body JSON du frontend et le transmet à Anthropic
    avec la clé API stockée côté serveur.
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Clé API Anthropic non configurée sur le serveur."
        )

    body = await request.json()

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

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Erreur Anthropic : {response.text[:300]}"
        )

    return response.json()


# Servir le fichier HTML statique si présent dans le même dossier
@app.get("/")
def serve_frontend():
    html_path = os.path.join(os.path.dirname(__file__), "pipeline_doc_dq_tool.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Frontend non trouvé. Placez pipeline_doc_dq_tool.html dans le même dossier."}


if __name__ == "__main__":
    import uvicorn
    print("=" * 55)
    print("  Pipeline Doc + DQ Analyzer — Serveur proxy")
    print("=" * 55)
    print(f"  Clé API : {'✓ configurée' if ANTHROPIC_API_KEY else '✗ MANQUANTE'}")
    print(f"  URL     : http://localhost:8000")
    print(f"  Health  : http://localhost:8000/health")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8000)
