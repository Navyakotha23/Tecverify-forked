FROM python:3-slim
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
# HTTP backend without certs and without timeout
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "server:app" ]

# HTTPS backend with certs and without timeout
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "--certfile", "/certs/cert.crt", "--keyfile", "/certs/pvt_key.key", "server:app" ]

# HTTP backend without certs and with timeout
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "server:app", "--timeout", "600" ] 

# HTTPS backend with certs and with timeout
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "--certfile", "/certs/cert.crt", "--keyfile", "/certs/pvt_key.key", "server:app", "--timeout", "600" ] 
