import logging
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Endpoint Conversaciones",
    description="Recibe eventos de chatbots (Infobip) y los guarda en Google Sheets",
    version="1.0.0",
)

DEFAULT_CHATBOT_SHEET = "envioformal"


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "endpoint-conversaciones"}


@app.post("/webhooks/infobip/call-api")
async def infobip_call_api_webhook(request: Request, sheet_name: str = DEFAULT_CHATBOT_SHEET):
    try:
        from backend.services.google_sheets_service import GoogleSheetsService

        payload: Any = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="El body debe ser un JSON tipo objeto")

        row = {
            "received_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": "infobip_call_api",
            "sheet_name": sheet_name,
            **payload,
        }

        sheets_service = GoogleSheetsService()
        sheets_service.append_dict_row(sheet_name=sheet_name, data=row)

        return {
            "success": True,
            "sheet_name": sheet_name,
            "message": "Payload guardado en Google Sheets",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error guardando webhook en sheet '%s': %s", sheet_name, str(e))
        raise HTTPException(status_code=500, detail=str(e))
