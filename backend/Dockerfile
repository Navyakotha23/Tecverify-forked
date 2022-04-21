FROM python:3-slim
WORKDIR /usr/src/app
# We are in /usr/src/app folder. Copying contents of BE folder(Dockerfile is in BE folder) to /usr/src/app folder  
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
# Changing the directory to /usr/scr/app/src to run server.py 
# HTTP backend without certs and without timeout
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "server:app" ]

# HTTPS backend with certs and without timeout
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "--certfile", "/certs/cert.crt", "--keyfile", "/certs/pvt_key.key", "server:app" ]

# HTTP backend without certs and with timeout
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "server:app", "--timeout", "600" ] 

# HTTPS backend with certs and with timeout
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "--certfile", "/certs/cert.crt", "--keyfile", "/certs/pvt_key.key", "server:app", "--timeout", "600" ] 
