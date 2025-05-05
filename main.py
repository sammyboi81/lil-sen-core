from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
import json, os, logging

from supabase_client import log_lead_to_db, upsert_agent_to_db, get_supabase_client
from supabase import Client

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lil Sen Core Backend",
    description="API for logging leads and managing agent registration.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LeadData(BaseModel):
    source: str
    contact_info: Optional[str] = None
    email: Optional[EmailStr] = None
    message: Optional[str] = None
    misc_data: Optional[dict] = None

class AgentData(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    registered_at: datetime = Field(default_factory=datetime.utcnow)

@app.get("/heartbeat")
def heartbeat():
    logger.info("Heartbeat pinged")
    return {"status": "OK", "timestamp": datetime.utcnow().isoformat()}

@app.post("/log-lead")
async def log_lead_endpoint(lead: LeadData, supabase: Client = Depends(get_supabase_client)):
    if not supabase:
        raise HTTPException(status_code=503, detail="Database client not available.")
    logger.info(f"Received lead: {lead.model_dump()}")
    lead_data = lead.model_dump()
    lead_data["received_at"] = datetime.utcnow().isoformat()
    inserted = await log_lead_to_db(lead_data)
    if inserted:
        return {"ok": True, "data": inserted}
    raise HTTPException(status_code=500, detail="Failed to log lead.")

@app.get("/register")
async def register_agent_from_file(supabase: Client = Depends(get_supabase_client)):
    path = "chuck_identity.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Identity file not found.")
    try:
        with open(path, 'r') as f:
            raw = json.load(f)
        agent = AgentData(**raw).model_dump()
        agent["registered_at"] = agent["registered_at"].isoformat()
        upserted = await upsert_agent_to_db(agent)
        if upserted:
            return {"ok": True, "data": upserted}
        raise HTTPException(status_code=500, detail="Supabase upsert failed.")
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed.")
'''

# Save it
main_py_path = "/mnt/data/main.py"
with open(main_py_path, "w") as f:
    f.write(main_py_code.strip())

main_py_path
