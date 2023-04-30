import envImport  # has to be first
from API.server import Server
from fastapi import FastAPI

app = FastAPI()
s = Server('faces')
app.include_router(s.router)
