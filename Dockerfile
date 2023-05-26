#!/bin/bash

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY . /app
COPY ./data_access /app/data_access
COPY ./migrations /app/migrations
COPY alembic.ini /app/alembic.ini
COPY migrations /app/migrations
COPY models.db /app/models.db
COPY ./app_routers/auth.py /app/app_routers/auth.py
COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    python3-setuptools \
    gcc

RUN apt-get update

# Create a virtual environment in /opt
RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/pip install gunicorn
RUN /opt/venv/bin/pip install -r /app/requirements.txt

#RUN apt-get remove -y --purge make gcc build-essential \
#    && apt-get autoremove -y \
#    && rm -rf /var/lib/apt/lists/*


RUN chmod +x entrypoint.sh
CMD [ "/opt/venv/bin/gunicorn","-k uvicorn.workers.UvicornWorker","app:server","--bind","0.0.0.0:8000" ]
