import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self):
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        if not self.spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_ID no esta configurado")

        credentials_info = self._get_credentials_info()
        creds = Credentials.from_service_account_info(credentials_info, scopes=self.SCOPES)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)

    def _get_credentials_info(self) -> dict:
        credentials_raw = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "")
        if not credentials_raw:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS no esta configurado")

        candidate = credentials_raw.strip()

        # Soporta pegar el valor como:
        # GOOGLE_SHEETS_CREDENTIALS={...json...}
        if candidate.startswith("GOOGLE_SHEETS_CREDENTIALS="):
            candidate = candidate.split("=", 1)[1].strip()

        # Soporta JSON envuelto entre comillas
        if (candidate.startswith("'") and candidate.endswith("'")) or (
            candidate.startswith('"') and candidate.endswith('"')
        ):
            candidate = candidate[1:-1]

        try:
            credentials_info = json.loads(candidate)
        except json.JSONDecodeError as e:
            raise ValueError(f"GOOGLE_SHEETS_CREDENTIALS invalido: {e}") from e

        if "private_key" in credentials_info:
            credentials_info["private_key"] = credentials_info["private_key"].replace("\\n", "\n")
        return credentials_info

    def append_dict_row(self, sheet_name: str, data: Dict[str, Any]) -> bool:
        if not data:
            raise ValueError("No hay datos para guardar en Google Sheets")

        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(
                title=sheet_name,
                rows=1000,
                cols=max(20, len(data) + 10),
            )

        existing_headers = worksheet.row_values(1)
        if not existing_headers or existing_headers == [""]:
            existing_headers = list(data.keys())
            worksheet.update("A1", [existing_headers])
        else:
            missing_headers = [key for key in data.keys() if key not in existing_headers]
            if missing_headers:
                existing_headers.extend(missing_headers)
                worksheet.update("A1", [existing_headers])

        row = [self._normalize_sheet_value(data.get(header, "")) for header in existing_headers]
        worksheet.append_row(row, value_input_option="USER_ENTERED")

        logger.info("Fila agregada en hoja '%s'", sheet_name)
        return True

    @staticmethod
    def _normalize_sheet_value(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
