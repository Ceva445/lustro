from fastapi import FastAPI
from app.routers.ksiengowy import router as ksiengowy_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Global cache
app.state.cache = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ksiengowy_router, prefix="/api", tags=["ksiengowy"])

@app.get("/")
async def root():
    return {"message": "FastAPI project is running"}