#!/bin/bash

set -e

if [[ "${MODE}" == "worker" ]]; then
  CONCURRENCY_OPTION="-c ${CELERY_WORKER_AMOUNT:-4}"
  exec celery -A app.core.worker worker $CONCURRENCY_OPTION --loglevel ${LOG_LEVEL:-INFO}

elif [[ "${MODE}" == "beat" ]]; then
  exec celery -A app.core.worker beat --loglevel ${LOG_LEVEL:-INFO}

else
  uvicorn main:app \
    --host ${HOST:-0.0.0.0} --port ${PORT:-8000} \
    --workers ${SERVER_WORKER_AMOUNT:-4}
    --timeout ${GUNICORN_TIMEOUT:-200}
fi