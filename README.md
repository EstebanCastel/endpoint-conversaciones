# Endpoint Conversaciones

Servicio FastAPI para recibir payloads desde Infobip Call API y guardarlos en Google Sheets.

## Endpoint

- `POST /webhooks/infobip/call-api?sheet_name=envioformal`
- `Content-Type: application/json`

Ejemplo body:

```json
{
  "chatbot": "oferta_habi",
  "event": "reply_button_click",
  "button_text": "Tu Oferta",
  "contact": "+573001112233"
}
```

Notas:
- `sheet_name` es dinámico para reutilizar el endpoint para varios chatbots.
- Si la hoja no existe, se crea automáticamente.
- Si llegan nuevas llaves en el JSON, se agregan como nuevas columnas.

## Variables de entorno

- `GOOGLE_SHEETS_ID`
- `GOOGLE_SHEETS_CREDENTIALS`

## Correr local

```bash
pip install -r requirements.txt
cp .env.example .env
./start.sh
```

Healthcheck:

```bash
GET /health
```
