"""
main.py
=======

Module principal pour l'exécution de l'API via uvicorn.

Dependencies:
    fastapi: Module principal pour créer des API REST avec documentation automatique.
"""

from fastapi import FastAPI

from API_DATABASE import auth_api
from CRM_DATABASE import crm_api
from CRM_CLIENT_MANIFEST import manifest_api

app = FastAPI(title="CRM API", version="1.1.0")

# Inclusion des routers pour les différentes parties de l'API
app.include_router(auth_api.auth_router)
app.include_router(crm_api.crm_router)
app.include_router(manifest_api.manifest_router)


@app.get("/")
def root() -> dict:
    """Point d'entrée racine de l'API.

    Returns:
        dict: Message de bienvenue pour l'API.
    """
    return {"message": "Welcome to CRM API!"}
