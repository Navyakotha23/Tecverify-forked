FROM python:3-slim
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "server:app" ]
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src/", "--certfile", "/certs/cert.crt", "--keyfile", "/certs/pvt_key.key", "server:app" ]
