#!/bin/bash

/opt/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker --workers 5 app:server --bind "0.0.0.0:8000"