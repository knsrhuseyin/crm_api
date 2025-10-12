import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

from API_DATABASE import auth_api, auth_manage_user
from API_DATABASE.auth import user_dependency
from CRM_DATABASE import crm_api


app = FastAPI(title="CRM API")
app.include_router(auth_api.auth_router)
app.include_router(crm_api.crm_router)
#app.include_router(auth_manage_user.auth_manage_user_router)


@app.get("/")
def root(request: Request):
    current_user: user_dependency = None
    if current_user is None:
        raise HTTPException(status_code=401, detail=f'Authentication Failed !')
    return {"Current User": current_user}


