FROM ubuntu:20.04
#
# docker build -t valeron12345/flask_app:1.0.0 .
# docker push valeron12345/flask_app:1.0.0
# docker build -t valeron12345/flask_app:latest .
# docker push valeron12345/flask_app:latest
#
ENV FLASK_APP=flask_app

RUN apt-get update -y && \
    apt-get install -y python3-pip python-dev libmysqlclient-dev

COPY . /app

WORKDIR /app

RUN pip install -r requirments.txt

ENTRYPOINT [ "python3" ]

CMD [ "flask_app.py" ]
