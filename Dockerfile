FROM --platform=linux/amd64 python:3.8-slim

ADD ./requirements.txt /mutable/requirements.txt
WORKDIR /mutable

ADD mutable /mutable/mutable

RUN pip install -r requirements.txt

ENTRYPOINT [ "gunicorn" ]
