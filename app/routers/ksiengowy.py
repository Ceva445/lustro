from fastapi import APIRouter, Request, HTTPException
from app.schemas import NgrokRequest, AdapterRequest
import httpx

router = APIRouter()

headers = {
    "ngrok-skip-browser-warning": "anyvalue",
    "User-Agent": "FastAPI-Adapter/1.0"
}

@router.post("/ksiengowy/add_url")
async def add_ngrok_url(request: Request, data: NgrokRequest):
    """
    Receives JSON {"ngrok_url": "..."} and adds/updates it in the global cache.
    """
    cache = request.app.state.cache
    cache["ngrok_url"] = data.ngrok_url

    return {
        "status": "success",
        "cached_value": cache["ngrok_url"]
    }

@router.get("/ksiengowy/get_url")
async def get_ngrok_url(request: Request):
    """
    Returns the saved ngrok_url from the global cache.
    """
    cache = request.app.state.cache

    ngrok_url = cache.get("ngrok_url")
    if not ngrok_url:
        raise HTTPException(status_code=404, detail="ngrok_url not found in cache")

    return {
        "ngrok_url": ngrok_url
    }

@router.post("/ksiengowy/adapter")
async def ksiengowy_adapter(request: Request, data: AdapterRequest):
    """
    Accepts JSON and forwards it to the URL stored in the global cache.
    """
    cache = request.app.state.cache

    # Check if URL exists in cache
    ngrok_url = cache.get("ngrok_url")
    if not ngrok_url:
        raise HTTPException(status_code=400, detail="ngrok_url is not set in cache")

    # Form the target URL for forwarding
    target_url = f"{ngrok_url}/{data.doc_type}"
    payload = data.model_dump()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(target_url, json=payload, headers=headers)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "forwarded",
        "target": target_url,
        "response_status": response.status_code,
        "response_data": response.json() if response.content else None
    }