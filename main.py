"""
main.py
=======

Module principal permettant l'exécution de l'API via uvicorn.

Dependencies:
    fastapi: Module principal du programme permettant de créer des API REST avec une documentation créé automatiquement.
"""
from fastapi import FastAPI

from API_DATABASE import auth_api
from CRM_DATABASE import crm_api
from CRM_CLIENT_MANIFEST import manifest_api

app = FastAPI(title="CRM API", version="1.0")
app.include_router(auth_api.auth_router)
app.include_router(crm_api.crm_router)
app.include_router(manifest_api.manifest_router)


@app.get("/")
def root():
    """
    Fonction root de l'API renvoyant un message via une requête à l'URL brute.
    """
    return {"message": "Welcome to CRM API!"}
