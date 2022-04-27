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

# Harcoded certs for BE. i.e. created a certs folder(be-certs) in BE and that folder will be copied to BE image.
# Now we cannot mount certs for BE though volumes in docker-compose. Harcoded certs folder will be used. 
# certs given through nginx are for FE and certs hardcoded for BE are different because certs for nginx may be the proper certs given by the client.
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "--certfile", "/usr/src/app/be-certs/cert.crt", "--keyfile", "/usr/src/app/be-certs/pvt_key.key", "server:app", "--timeout", "600" ] 

# Test to take certs dynamically
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "--certfile", "/certs/*.crt", "--keyfile", "/certs/*.key", "server:app", "--timeout", "600" ]


# # Test to bind with 443
# EXPOSE 443
# # HTTPS backend binding with 443 with certs and with timeout
# CMD [ "gunicorn", "--bind", "0.0.0.0:443", "--chdir", "./src/", "--certfile", "/certs/cert.crt", "--keyfile", "/certs/pvt_key.key", "server:app", "--timeout", "600" ]
