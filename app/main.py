from fastapi import FastAPI
from app.database import engine
from app.routers.ksiengowy import router as ksiengowy_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.state.cache = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ksiengowy_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "FastAPI running"}
