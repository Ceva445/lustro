from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks, Request
from app.schemas import NgrokRequest, AdapterRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import NgrokURL
from app.database import get_db
import httpx

router = APIRouter()

headers = {
    "ngrok-skip-browser-warning": "anyvalue",
    "User-Agent": "FastAPI-Adapter/1.0"
}


@router.post("/ksiengowy/add_url")
async def add_ngrok_url(
    request: Request,
    data: NgrokRequest,
    db: AsyncSession = Depends(get_db)
):
    cache = request.app.state.cache

    # Read record (async)
    result = await db.execute(select(NgrokURL).where(NgrokURL.id == 1))
    record = result.scalar_one_or_none()

    if record:
        record.url = data.ngrok_url
    else:
        record = NgrokURL(id=1, url=data.ngrok_url)
        db.add(record)

    await db.commit()

    cache["ngrok_url"] = data.ngrok_url
    return {
        "status": "success", 
        "ngrok_url": data.ngrok_url
        }


@router.get("/ksiengowy/get_url")
async def get_ngrok_url(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    cache = request.app.state.cache

    # cache first
    url = cache.get("ngrok_url")
    if url:
        return {"ngrok_url": url}

    # DB lookup
    result = await db.execute(select(NgrokURL).where(NgrokURL.id == 1))
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="ngrok_url not found")

    cache["ngrok_url"] = record.url
    return {"ngrok_url": record.url}


@router.post("/ksiengowy/adapter")
async def ksiengowy_adapter(
    request: Request,
    data: AdapterRequest,
    background_tasks: BackgroundTasks
):
    """
    Accepts JSON and forwards it to the URL stored in the global cache.
    The AdapterRequest now includes wait_response: bool to control behavior.
    """

    cache = request.app.state.cache

    # Check if URL exists in cache
    ngrok_url = cache.get("ngrok_url")
    if not ngrok_url:
        raise HTTPException(status_code=400, detail="ngrok_url is not set in cache")

    # Form the target URL for forwarding
    target_url = f"{ngrok_url}/{data.doc_type}"

    # Exclude wait_response from the forwarded payload
    payload = data.model_dump(exclude={"wait_response", "doc_type"})

    # Fire-and-forget forwarding task
    async def forward_task():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                await client.post(target_url, json=payload, headers=headers)
            except Exception as e:
                print(f"Forwarding error: {e}")

    if not data.wait_response:
        background_tasks.add_task(forward_task)

        return {
            "status": "forwarded",
            "target": target_url,
            "mode": "fire-and-forget"
        }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(target_url, json=payload, headers=headers)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "forwarded",
        "target": target_url,
        "mode": "wait-response",
        "response_status": response.status_code,
        "response_data": response.json() if response.content else None
    }
