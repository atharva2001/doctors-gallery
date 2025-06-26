FROM python:3.12-slim

WORKDIR /health_reminder_system/auth_service

# RUN apt-get update && apt-get install -y \
#     gcc \
#     libpq-dev \
#     redis-server

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt 

EXPOSE 8000

COPY . .


# gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000

CMD [ "gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0:8000" ]