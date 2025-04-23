from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import uuid
import datetime
import os

app = FastAPI()

class Command(BaseModel):
    agent_name: str
    purpose: str
    functions: list[str]
    tone: str = "friendly"

@app.post("/create-agent")
async def create_agent(cmd: Command):
    agent_id = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat()

    payload = {
        "id": agent_id,
        "name": cmd.agent_name,
        "purpose": cmd.purpose,
        "functions": cmd.functions,
        "tone": cmd.tone,
        "created_at": timestamp
    }

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{supabase_url}/rest/v1/agents",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=payload
        )

    return {"status": "agent created", "id": agent_id, "response": response.json()}
