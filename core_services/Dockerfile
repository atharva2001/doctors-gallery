FROM python:3.12-slim

WORKDIR /auth_service/core_services

# RUN  apt-get update

# RUN apt-get install gnupg curl

# RUN curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
#       gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
#       --dearmor

# RUN echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list

# RUN  apt-get update

# RUN  apt-get install -y mongodb-org



COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt 

EXPOSE 8001

COPY . .


# # gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000

CMD [ "gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8001" ]


