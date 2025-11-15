from pydantic import BaseModel

class NgrokRequest(BaseModel):
    ngrok_url: str

class AdapterRequest(BaseModel):
    doc_type: str
    file_url: str
    forward_url: str