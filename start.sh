#!/usr/bin/env bash
set -euo pipefail
exec uvicorn backend.api.ctl_api:app --host 0.0.0.0 --port ${PORT:-8000}
