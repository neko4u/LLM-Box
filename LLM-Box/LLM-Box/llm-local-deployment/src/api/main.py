from fastapi import FastAPI
from .routes import router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Perform any startup tasks here, such as loading models or initializing resources
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Perform any cleanup tasks here, such as closing connections or saving state
    pass

app.include_router(router)